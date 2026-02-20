import requests
from colorama import Fore, Back, Style, init
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from ascii_magic import AsciiArt

# Colorama for colored input prompt only
init(autoreset=True)

# Rich console for beautiful output
console = Console()

api = "https://api.github.com/users/"

console.print(Panel(
    "[bold magenta]GitHub User Lookup Tool[/] 🚀\nEnter a username below (or 'q' to quit)",
    style="bright_blue on black",
    expand=False
))

while True:
    # Colored prompt with colorama
    username_input = Back.BLUE + Fore.WHITE + "\nGitHub username: " + Style.RESET_ALL
    username = input(username_input).strip()

    if username.lower() in ['q', 'quit', 'exit', '']:
        if username == '':
            console.print("[italic red]No username entered.[/]")
            continue
        console.print("[yellow bold]Goodbye! 👋[/yellow bold]")
        break

    try:
        response = requests.get(api + username, timeout=12)
        response.raise_for_status()  # Raises exception for bad status
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error fetching data:[/] {str(e)} 😕")
        continue

    if response.status_code == 200:
        data = response.json()

        # ────────────────────────────────────────────────
        # Main profile table
        table = Table(show_header=False, expand=True, border_style="bright_blue", padding=(0, 1))
        table.add_column("Field", style="bold cyan", width=20)
        table.add_column("Value", style="white")

        table.add_row("Name", data.get('name', '—') or '—')
        table.add_row("Bio", f"[italic]{data.get('bio', 'No bio provided')}[/]" or '—')
        table.add_row("Location", data.get('location', '—') or '—')
        table.add_row("Company", data.get('company', '—') or '—')
        table.add_row("Blog", f"[link={data.get('blog','') or ''}]{data.get('blog', '—')}[/link]" or '—')
        table.add_row("Twitter", f"@{data['twitter_username']}" if data.get('twitter_username') else '—')
        table.add_row("Email", data.get('email', '—') or '—')
        table.add_row("Public Repos", f"[green]{data.get('public_repos', 0):,}[/]")
        table.add_row("Followers", f"[magenta]{data.get('followers', 0):,}[/]")
        table.add_row("Following", f"[yellow]{data.get('following', 0):,}[/]")
        table.add_row("Public Gists", str(data.get('public_gists', 0)))
        table.add_row("Hireable", "[green]Yes[/green]" if data.get('hireable') else "[red]No[/red]")
        table.add_row("Joined GitHub", data['created_at'][:10] if data.get('created_at') else '—')
        table.add_row("Profile", f"[underline blue]{data['html_url']}[/]")

        console.print(Panel(
            table,
            title=f"  [bold magenta]{username.upper()} on GitHub[/]  ",
            subtitle=f"[dim]ID: {data['id']} • Type: {data['type']}[/dim]",
            border_style="bright_magenta",
            padding=(1, 2),
            expand=True
        ))

        # ────────────────────────────────────────────────
        #List all public repository names + star count
        console.print("\n[bold cyan]Public Repositories (Name & Stars):[/]")

        repos = []
        page = 1
        while True:
            try:
                repo_url = f"https://api.github.com/users/{username}/repos"
                params = {
                    "per_page": 100,
                    "page": page,
                    "sort": "updated",          
                    "direction": "desc"
                }
                repo_response = requests.get(repo_url, params=params, timeout=10)
                repo_response.raise_for_status()
                page_data = repo_response.json()

                if not page_data:  # empty page → end
                    break

                repos.extend(page_data)
                page += 1

            except requests.exceptions.RequestException as e:
                console.print(f"[bold red]Failed to load repositories:[/] {str(e)}")
                break

        if not repos:
            console.print("[italic dim]No public repositories found.[/]")
        else:
            repo_table = Table(show_header=True, header_style="bold magenta", expand=True)
            repo_table.add_column("Repository Name", style="cyan", no_wrap=True)
            repo_table.add_column("Stars", justify="right", style="yellow")

            for repo in repos:
                repo_table.add_row(
                    repo["name"],
                    f"{repo['stargazers_count']:,}" if repo["stargazers_count"] > 0 else "—"
                )

            console.print(repo_table)
            console.print(f"\n[dim italic]Total public repositories: {len(repos)}[/]")

        # ────────────────────────────────────────────────
        # Avatar preview
        avatar = data.get('avatar_url')
        if avatar:
            try:
                my_art = AsciiArt.from_url(avatar)
                console.print("\n[bold cyan]Profile Picture Preview (ASCII):[/]")

                my_art.to_terminal(
                    columns=80,
                    width_ratio=2.0,
                    enhance_image=True,
                    char=' .,:;i1tfLCG08%@'
                )
            except Exception as e:
                console.print("[dim yellow]Avatar render failed:[/]", str(e))
                console.print(f"[dim]Direct link: [link={avatar}]{avatar}[/link][/dim]")

        console.print("\n[bold green]✓ Profile loaded successfully![/] 🎉")
        console.print("[dim]─" * 70 + "\n")

    else:

        console.print("[bold red]User not found.[/] Try another username. 😕\n")
