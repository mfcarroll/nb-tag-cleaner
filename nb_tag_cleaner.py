import argparse
import json
import sys

import requests
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

DEFAULT_PREFIXES = ["Department:", "Job:", "Location:", "Region", "Status:"]


class NationBuilderCleanerV2:
    def __init__(self, slug, token, dry_run=False):
        self.slug = slug
        self.base_url = f"https://{slug}.nationbuilder.com/api/v2"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_all_tags(self):
        """
        Fetches all signup tags using API v2 with pagination.
        """
        print(f"{Fore.CYAN}Fetching all tags via API v2... (this may take a moment)")
        tags = []

        # Initial URL
        url = f"{self.base_url}/signup_tags"
        params = {"page[size]": "100"}

        while url:
            try:
                # If following a 'next' link, clear params to avoid duplication
                if "page[" in url:
                    params = {}

                response = self.session.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("data", [])

                    for item in results:
                        tags.append(
                            {"id": item["id"], "name": item["attributes"]["name"]}
                        )

                    # Pagination Handling
                    links = data.get("links", {})
                    next_link = links.get("next")

                    if next_link:
                        # Handle relative URLs
                        if next_link.startswith("/"):
                            url = f"https://{self.slug}.nationbuilder.com{next_link}"
                        elif next_link.startswith("http"):
                            url = next_link
                        else:
                            url = f"https://{self.slug}.nationbuilder.com/api/v2/{next_link}"
                    else:
                        url = None

                else:
                    print(
                        f"{Fore.RED}Error fetching tags: {response.status_code} - {response.text}"
                    )
                    break
            except Exception as e:
                print(f"{Fore.RED}Connection error: {e}")
                sys.exit(1)

        return tags

    def delete_tag(self, tag_id, tag_name):
        """
        Deletes the tag definition entirely using API v2.
        """
        if self.dry_run:
            print(f"{Fore.YELLOW}[DRY RUN] Would delete tag ID {tag_id} ('{tag_name}')")
            return True

        url = f"{self.base_url}/signup_tags/{tag_id}"
        response = self.session.delete(url)

        if response.status_code in [200, 204]:
            print(f"{Fore.GREEN}Deleted '{tag_name}' (ID: {tag_id})")
            return True
        else:
            print(
                f"{Fore.RED}Failed to delete '{tag_name}' (ID: {tag_id}): {response.status_code} - {response.text}"
            )
            return False

    def run(self, prefixes, delete_all=False):
        # 1. Fetch Tags
        all_tags = self.get_all_tags()
        if not all_tags:
            print("No tags found or access denied.")
            return

        # 2. Filter Tags
        tags_to_delete = []
        if delete_all:
            tags_to_delete = all_tags
        else:
            for tag in all_tags:
                if any(tag["name"].startswith(prefix) for prefix in prefixes):
                    tags_to_delete.append(tag)

        if not tags_to_delete:
            print(f"{Fore.GREEN}No tags found matching the specified prefixes.")
            return

        # 3. Confirmation
        # Sort so tags with a ':' are grouped first, then alphabetically.
        tags_to_delete = sorted(
            tags_to_delete, key=lambda x: (":" not in x["name"], x["name"].casefold())
        )

        print(f"\n{Fore.WHITE}Found {len(tags_to_delete)} tags matching criteria:")
        print(f"{Fore.WHITE}------------------------------------------------")
        for index, tag in enumerate(tags_to_delete, start=1):
            print(f"{Fore.RED}{index}. {tag['name']} {Fore.BLACK}(ID: {tag['id']})")
        print(f"{Fore.WHITE}------------------------------------------------")

        if self.dry_run:
            prompt_text = f"{Fore.YELLOW}[DRY RUN MODE] Confirm to simulate deletion of these tags? (yes/no): {Style.RESET_ALL}"
        else:
            prompt_text = f"{Fore.RED}WARNING: This will permanently delete these tags and untag all associated people.\nAre you sure you want to proceed? (yes/no): {Style.RESET_ALL}"

        confirm = input(prompt_text)

        if confirm.lower() != "yes":
            print("Operation cancelled.")
            return

        # 4. Execution
        print(f"\n{Fore.CYAN}Starting deletion process...")
        count = 0

        for tag in tags_to_delete:
            success = self.delete_tag(tag["id"], tag["name"])
            if success:
                count += 1

        print(f"\n{Fore.GREEN}Success! Processed {count} tags.")


def load_config(config_path):
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}Config file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"{Fore.RED}Invalid JSON in config file.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Delete specific tags from NationBuilder (API v2)."
    )
    parser.add_argument("--slug", help="Your NationBuilder nation slug")
    parser.add_argument("--token", help="Your Developer API Token")
    parser.add_argument("--config", help="Path to a JSON configuration file")
    parser.add_argument(
        "--delete-all",
        action="store_true",
        help="Delete ALL tags in the nation (Dangerous!)",
    )
    parser.add_argument("--prefixes", nargs="+", help="List of tag prefixes to delete")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate deletion without making changes",
    )

    args = parser.parse_args()

    slug = args.slug
    token = args.token
    prefixes = None
    delete_all = args.delete_all

    # Load from config if available
    if args.config:
        config = load_config(args.config)
        if not slug:
            slug = config.get("slug")
        if not token:
            token = config.get("token")
        if args.prefixes:
            # CLI override
            prefixes = args.prefixes
            prefix_source = "Command Line Override"
        elif "prefixes" in config:
            # Config file
            prefixes = config.get("prefixes")
            prefix_source = "Config File"

        if not args.delete_all:
            delete_all = config.get("delete_all", False)
    else:
        # CLI only
        prefixes = args.prefixes or DEFAULT_PREFIXES
        prefix_source = "Command Line / Defaults"

    if not slug or not token:
        print(f"{Fore.RED}Error: Nation slug and API token are required.")
        sys.exit(1)

    # --- CONFIG SUMMARY ---
    print(f"\n{Fore.WHITE}=== Configuration Loaded ===")
    print(f"{Fore.BLUE}Nation Slug:   {Fore.WHITE}{slug}")
    print(f"{Fore.BLUE}Token:         {Fore.WHITE}{token[:4]}...{token[-4:]} (Masked)")
    print(
        f"{Fore.BLUE}Mode:          {Fore.YELLOW if args.dry_run else Fore.RED}{'DRY RUN (Simulation)' if args.dry_run else 'LIVE EXECUTION'}"
    )

    if delete_all:
        print(f"{Fore.RED}Target:        ALL TAGS (Dangerous!)")
    else:
        print(f"{Fore.BLUE}Prefix Source: {Fore.WHITE}{prefix_source}")
        print(f"{Fore.BLUE}Prefixes:      {Fore.WHITE}{prefixes}")
    print(f"{Fore.WHITE}============================\n")
    # ----------------------

    cleaner = NationBuilderCleanerV2(slug, token, dry_run=args.dry_run)
    cleaner.run(prefixes, delete_all)
