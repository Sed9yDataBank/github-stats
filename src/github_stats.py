import requests
from datetime import datetime, timedelta
import calendar
import os
from typing import Dict, List, Tuple
import logging
from collections import defaultdict
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GitHubStats:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
        logger.info("GitHubStats initialized")

    def get_org_repos(self, org: str) -> List[str]:
        """Get all repositories in an organization."""
        logger.info(f"Fetching repositories for organization: {org}")
        repos = []
        page = 1
        while True:
            logger.info(f"Fetching page {page} of repositories")
            response = requests.get(
                f'{self.base_url}/orgs/{org}/repos',
                headers=self.headers,
                params={'page': page, 'per_page': 100}
            )
            if response.status_code != 200:
                logger.error(f"Failed to fetch repos: {response.text}")
                raise Exception(f"Failed to fetch repos: {response.text}")
            
            data = response.json()
            if not data:
                break
                
            repos.extend([repo['name'] for repo in data])
            logger.info(f"Found {len(data)} repositories on page {page}")
            page += 1
            
        logger.info(f"Total repositories found: {len(repos)}")
        return repos

    def get_user_commits(self, org: str, username: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get all commits by a user in an organization's repositories within a date range."""
        logger.info(f"Fetching commits for user {username} from {start_date} to {end_date}")
        all_commits = []
        repos = self.get_org_repos(org)
        
        for repo in repos:
            logger.info(f"Checking commits in repository: {repo}")
            page = 1
            while True:
                logger.info(f"Fetching page {page} of commits for {repo}")
                response = requests.get(
                    f'{self.base_url}/repos/{org}/{repo}/commits',
                    headers=self.headers,
                    params={
                        'author': username,
                        'since': start_date.isoformat(),
                        'until': end_date.isoformat(),
                        'page': page,
                        'per_page': 100
                    }
                )
                
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch commits for {repo}: {response.text}")
                    break
                
                data = response.json()
                if not data:
                    break
                    
                all_commits.extend(data)
                logger.info(f"Found {len(data)} commits on page {page} for {repo}")
                page += 1
                
        logger.info(f"Total commits found: {len(all_commits)}")
        return all_commits

    def get_commit_stats(self, org: str, username: str, year: int, month: int) -> Tuple[int, int, Dict]:
        """Get total additions and deletions for a user in a specific month."""
        logger.info(f"Calculating stats for {username} in {org} for {year}-{month}")
        # Calculate date range
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        commits = self.get_user_commits(org, username, start_date, end_date)
        
        total_additions = 0
        total_deletions = 0
        repo_stats = defaultdict(lambda: {'additions': 0, 'deletions': 0, 'commits': 0})
        daily_stats = defaultdict(lambda: {'additions': 0, 'deletions': 0, 'commits': 0})
        commit_times = []
        
        logger.info(f"Processing {len(commits)} commits for detailed stats")
        for i, commit in enumerate(commits, 1):
            commit_sha = commit['sha']
            commit_url = commit['url']
            repo_name = commit_url.split('/repos/')[1].split('/commits/')[0].split('/')[-1]
            commit_date = datetime.strptime(commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
            commit_times.append(commit_date)
            
            logger.info(f"Processing commit {i}/{len(commits)}: {commit_sha[:7]} in {repo_name}")
            
            response = requests.get(
                f'{self.base_url}/repos/{org}/{repo_name}/commits/{commit_sha}',
                headers=self.headers
            )
            
            if response.status_code == 200:
                stats = response.json()
                additions = stats['stats']['additions']
                deletions = stats['stats']['deletions']
                total_additions += additions
                total_deletions += deletions
                
                # Update repository stats
                repo_stats[repo_name]['additions'] += additions
                repo_stats[repo_name]['deletions'] += deletions
                repo_stats[repo_name]['commits'] += 1
                
                # Update daily stats
                day_key = commit_date.strftime('%Y-%m-%d')
                daily_stats[day_key]['additions'] += additions
                daily_stats[day_key]['deletions'] += deletions
                daily_stats[day_key]['commits'] += 1
                
                logger.info(f"Commit {commit_sha[:7]}: +{additions} -{deletions}")
            else:
                logger.warning(f"Failed to get stats for commit {commit_sha[:7]}: {response.text}")
        
        logger.info(f"Final stats: +{total_additions} -{total_deletions}")
        return total_additions, total_deletions, {
            'repo_stats': dict(repo_stats),
            'daily_stats': dict(daily_stats),
            'commit_times': commit_times
        }

    def analyze_productivity(self, current_stats: Dict, previous_stats: Dict) -> Dict:
        """Analyze productivity metrics comparing current and previous month."""
        current_total = current_stats['additions'] + current_stats['deletions']
        previous_total = previous_stats['additions'] + previous_stats['deletions']
        
        # Calculate percentage changes
        total_change_pct = ((current_total - previous_total) / previous_total * 100) if previous_total > 0 else float('inf')
        additions_change_pct = ((current_stats['additions'] - previous_stats['additions']) / previous_stats['additions'] * 100) if previous_stats['additions'] > 0 else float('inf')
        deletions_change_pct = ((current_stats['deletions'] - previous_stats['deletions']) / previous_stats['deletions'] * 100) if previous_stats['deletions'] > 0 else float('inf')
        
        # Calculate daily averages
        current_daily_avg = current_total / len(current_stats['daily_stats']) if current_stats['daily_stats'] else 0
        previous_daily_avg = previous_total / len(previous_stats['daily_stats']) if previous_stats['daily_stats'] else 0
        
        # Calculate weekend vs weekday activity
        weekend_changes = 0
        weekday_changes = 0
        for day, stats in current_stats['daily_stats'].items():
            date = datetime.strptime(day, '%Y-%m-%d')
            if date.weekday() >= 5:  # Weekend
                weekend_changes += stats['additions'] + stats['deletions']
            else:
                weekday_changes += stats['additions'] + stats['deletions']
        
        # Calculate commit frequency
        commit_times = current_stats['commit_times']
        if len(commit_times) > 1:
            commit_intervals = [(commit_times[i] - commit_times[i-1]).total_seconds() 
                              for i in range(1, len(commit_times))]
            avg_commit_interval = statistics.mean(commit_intervals)
            commits_per_day = len(commit_times) / len(current_stats['daily_stats'])
        else:
            avg_commit_interval = 0
            commits_per_day = 0
        
        # Find most active repositories
        repo_activity = [(repo, stats['additions'] + stats['deletions']) 
                        for repo, stats in current_stats['repo_stats'].items()]
        repo_activity.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'total_change_percentage': total_change_pct,
            'additions_change_percentage': additions_change_pct,
            'deletions_change_percentage': deletions_change_pct,
            'daily_average_changes': current_daily_avg,
            'daily_average_change_percentage': ((current_daily_avg - previous_daily_avg) / previous_daily_avg * 100) if previous_daily_avg > 0 else float('inf'),
            'weekend_activity': weekend_changes,
            'weekday_activity': weekday_changes,
            'weekend_percentage': (weekend_changes / (weekend_changes + weekday_changes) * 100) if (weekend_changes + weekday_changes) > 0 else 0,
            'average_commit_interval_minutes': avg_commit_interval / 60,
            'commits_per_day': commits_per_day,
            'most_active_repositories': repo_activity[:5]
        }

def main():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Please set GITHUB_TOKEN environment variable")
        return

    stats = GitHubStats(token)
    
    org = input("Enter organization name: ")
    username = input("Enter GitHub username: ")
    year = int(input("Enter year (YYYY): "))
    month = int(input("Enter month (1-12): "))
    
    try:
        logger.info("Starting stats calculation...")
        
        # Get current month stats
        current_additions, current_deletions, current_stats = stats.get_commit_stats(org, username, year, month)
        
        # Get previous month stats
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1
            
        prev_additions, prev_deletions, prev_stats = stats.get_commit_stats(org, username, prev_year, prev_month)
        
        # Calculate productivity metrics
        productivity = stats.analyze_productivity(
            {'additions': current_additions, 'deletions': current_deletions, **current_stats},
            {'additions': prev_additions, 'deletions': prev_deletions, **prev_stats}
        )
        
        # Print results
        month_name = calendar.month_name[month]
        prev_month_name = calendar.month_name[prev_month]
        
        print(f"\n=== Stats for {username} in {org} ===")
        print(f"\nCurrent Month ({month_name} {year}):")
        print(f"Total additions: {current_additions}")
        print(f"Total deletions: {current_deletions}")
        print(f"Net changes: {current_additions - current_deletions}")
        
        print(f"\nPrevious Month ({prev_month_name} {prev_year}):")
        print(f"Total additions: {prev_additions}")
        print(f"Total deletions: {prev_deletions}")
        print(f"Net changes: {prev_additions - prev_deletions}")
        
        print("\n=== Productivity Analysis ===")
        print(f"Total changes: {productivity['total_change_percentage']:.1f}% {'increase' if productivity['total_change_percentage'] > 0 else 'decrease'}")
        print(f"Additions: {productivity['additions_change_percentage']:.1f}% {'increase' if productivity['additions_change_percentage'] > 0 else 'decrease'}")
        print(f"Deletions: {productivity['deletions_change_percentage']:.1f}% {'increase' if productivity['deletions_change_percentage'] > 0 else 'decrease'}")
        print(f"\nDaily Metrics:")
        print(f"Average changes per day: {productivity['daily_average_changes']:.1f}")
        print(f"Daily average change: {productivity['daily_average_change_percentage']:.1f}%")
        print(f"Commits per day: {productivity['commits_per_day']:.1f}")
        print(f"Average time between commits: {productivity['average_commit_interval_minutes']:.1f} minutes")
        
        print(f"\nWork Pattern Analysis:")
        print(f"Weekend activity: {productivity['weekend_activity']} changes ({productivity['weekend_percentage']:.1f}% of total)")
        print(f"Weekday activity: {productivity['weekday_activity']} changes ({100 - productivity['weekend_percentage']:.1f}% of total)")
        
        print("\nMost Active Repositories:")
        for repo, changes in productivity['most_active_repositories']:
            print(f"- {repo}: {changes} changes")
        
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
 