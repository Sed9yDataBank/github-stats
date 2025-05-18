# GitHub Stats

A Python tool to analyze GitHub commit statistics for users within an organization. This tool helps you track the number of additions and deletions made by a specific user across all repositories in an organization during a specified month, with detailed productivity metrics and month-over-month comparisons.

## Important Note on Metrics and Their Impact

This tool provides quantitative metrics about GitHub activity, but it's crucial to understand that these numbers are just one piece of the productivity puzzle. Software development productivity cannot be fully captured by commit statistics alone. Quality, impact, and value of work often transcend what can be measured in lines of code or commit frequency.

It's worth noting that if there was a clear, reliable way to measure software engineering productivity, GitHub - as the world's largest platform for software development - would have likely implemented such metrics directly into their product. The fact that they haven't done so speaks volumes about the complexity and nuance of measuring true developer productivity.

### Psychological Considerations

When metrics become known to team members, there's a natural human tendency to optimize for them, which can lead to unintended consequences:

- Developers might adjust their work patterns to appear more active
- The quality of commits might be compromised in favor of quantity
- Natural work rhythms might be disrupted to meet metric expectations
- The focus might shift from solving real problems to gaming the metrics

### Healthy Approach to Metrics

We recommend using these metrics with a light heart and as just one of many tools for understanding team activity. Consider them alongside other important factors like:

- Code quality and maintainability
- Business impact and value delivery
- Team collaboration and knowledge sharing
- Problem-solving effectiveness
- Technical leadership and mentorship

For a deeper understanding of software engineering metrics and their limitations, we recommend reading [GitClear's comprehensive guide on software engineering metrics](https://www.gitclear.com/popular_software_engineering_metrics_and_how_they_are_gamed).

Remember: The goal is to use metrics to inform and improve, not to create unnecessary pressure or competition. The best teams use metrics as a starting point for discussion, not as the final word on productivity or value.

## Features

- Fetch all repositories in a GitHub organization
- Get commit statistics for a specific user
- Calculate total additions and deletions
- Detailed logging of the process
- Support for pagination (handles large numbers of repositories and commits)
- Month-over-month comparison of changes
- Productivity metrics including:
  - Daily activity patterns
  - Weekend vs weekday work analysis
  - Commit frequency and intervals
  - Most active repositories
  - Changes per day statistics

## Prerequisites

- Python 3.6 or higher
- A GitHub Personal Access Token

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Sed9yDataBank/github-stats.git
cd github-stats
```

2. Install the required dependencies:
```bash
pip install requests
```

## Configuration

1. Create a GitHub Personal Access Token:
   - Go to GitHub Settings > Developer Settings > Personal Access Tokens
   - Generate a new token with the following permissions:
     - `repo` (Full control of private repositories)
     - `read:org` (Read organization data)

2. Set up your GitHub token as an environment variable:

For macOS/Linux:
```bash
export GITHUB_TOKEN='your_github_token'
```

For Windows (Command Prompt):
```bash
set GITHUB_TOKEN=your_github_token
```

For Windows (PowerShell):
```bash
$env:GITHUB_TOKEN='your_github_token'
```

To make the token permanent:
- For bash/zsh: Add the export command to your `~/.bashrc` or `~/.zshrc`
- For fish: Add the set command to your `~/.config/fish/config.fish`
- For Windows: Set it as a system environment variable

## Usage

Run the script:
```bash
python src/github_stats.py
```

The script will prompt you for:
1. Organization name
2. GitHub username
3. Year (YYYY)
4. Month (1-12)

If the GitHub token is not set, the script will:
1. Guide you through creating a token
2. Help you set it up for the current session
3. Provide instructions for making it permanent

## Output

The tool provides comprehensive statistics including:

### Current and Previous Month Comparison
- Total additions and deletions
- Net changes
- Percentage changes from previous month

### Productivity Analysis
- Total changes percentage increase/decrease
- Additions and deletions percentage changes
- Daily average changes
- Commit frequency metrics

### Work Pattern Analysis
- Weekend vs weekday activity
- Percentage of work done on weekends
- Average time between commits
- Commits per day

### Repository Analysis
- Top 5 most active repositories
- Changes per repository

Example output:
```
=== Stats for username in org ===

Current Month (April 2025):
Total additions: 27822
Total deletions: 8864
Net changes: 18958

Previous Month (March 2025):
Total additions: 25000
Total deletions: 8000
Net changes: 17000

=== Productivity Analysis ===
Total changes: 11.5% increase
Additions: 11.3% increase
Deletions: 10.8% increase

Daily Metrics:
Average changes per day: 1222.3
Daily average change: 5.2%
Commits per day: 6.7
Average time between commits: 215.4 minutes

Work Pattern Analysis:
Weekend activity: 5000 changes (15.2% of total)
Weekday activity: 27822 changes (84.8% of total)

Most Active Repositories:
- repo1: 15000 changes
- repo2: 8000 changes
- repo3: 5000 changes
```

## Logging

The tool provides detailed logging of its operations, including:
- Repository fetching progress
- Commit processing status
- API call results
- Error messages (if any)

Logs are displayed in the format:
```
YYYY-MM-DD HH:MM:SS,mmm - LEVEL - Message
```

## Error Handling

The tool handles various error cases:
- Invalid GitHub token
- Organization not found
- User not found
- API rate limiting
- Network issues

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
