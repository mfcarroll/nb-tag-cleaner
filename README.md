# NationBuilder Tag Cleaner

This tool is designed to bulk-delete tags from a NationBuilder instance based on specific prefixes. It supports local execution and can be deployed on PythonAnywhere for cloud-based interactive use.

## ⚙️ Configuration

The application uses a configuration file to manage settings such as your API credentials and target prefixes.

### 1. Generating a NationBuilder Developer API Token

To use this tool, you need a "Test Token" from NationBuilder. This is a short-lived key (expires in 24 hours) ideal for running specific cleanup tasks.

1.  Log in to your NationBuilder admin panel.
2.  Navigate to **Settings** > **Developer** > **API testing**.
3.  Click **New API token**
4.  Copy the token string provided (**▼** > **Copy token** ).
5.  Paste this token into your `config.json` file (see below).

Note that the token allows admin access to your NationBuilder account and should be protected carefully.

### 2. Creating the Config File

1.  Create a file named `config.json` in the root directory of the project.
2.  Use the structure below as a template:

```json
{
  "slug": "your-nation-slug",
  "token": "YOUR_API_TOKEN",
  "prefixes": [
    "Department:",
    "Job:",
    "Location:",
    "Region:",
    "Status:",
    "OldTag:"
  ],
  "delete_all": false
}
```

**Security Note:** Ensure `config.json` is added to your `.gitignore` file so sensitive keys are not committed to version control.

---

## 💻 Local Deployment & Usage

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### 2. Installation

Clone the repository and navigate to the project folder:

```bash
git clone https://github.com/mfcarroll/nb-tag-cleaner.git
cd nb-tag-cleaner
```

Create and activate a virtual environment:

- **Windows:**
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  python3 -m venv .venv
  source venv/bin/activate
  ```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Usage

**Run with a config file (Recommended):**

```bash
python nb_tag_cleaner.py --config config.json
```

**Run with a Dry Run (Simulate only):**

```bash
python nb_tag_cleaner.py --config config.json --dry-run
```

**Run with command line arguments (No config file):**

```bash
python nb_tag_cleaner.py --slug myslug --token mytoken --prefixes "Old:" "Temp:"
```

---

## ☁️ PythonAnywhere Deployment

The recommended way to deploy to PythonAnywhere is to host your code on GitHub and clone it to your PythonAnywhere account.

### 1. Initial Setup

1.  **Push to GitHub:** Ensure your latest local code is pushed to your GitHub repository.
2.  **Console Setup:** Log in to your PythonAnywhere dashboard, open a **Bash** console, and run the following commands:

    ```bash
    # Clone your repository
    git clone https://github.com/mfcarroll/nb-tag-cleaner.git
    cd nb-tag-cleaner

    # Create and activate a virtual environment
    python3 -m venv .venv

    # Install dependencies
    pip install -r requirements.txt
    ```

### 2. Updating Your Code

When you make changes on your local machine:

1.  Push changes to GitHub (`git push`).
2.  Go to your PythonAnywhere console and pull the changes:
    ```bash
    cd nb-tag-cleaner
    git pull origin main
    ```

---

## 🚀 Running on PythonAnywhere

This script is designed to be run interactively.

### Interactive Console Mode

Use this mode to interact with the script directly via the command line.

1.  Go to the **Consoles** tab on PythonAnywhere.
2.  Start a **Bash** console.
3.  Activate your virtual environment and run the script:
    ```bash
    cd nb-tag-cleaner
    source .venv/bin/activate
    python nb_tag_cleaner.py --config config.json
    ```

---

## 📝 Command Line Options

Below is a list of all available command-line arguments.

| Argument       | Description                                                                     |
| :------------- | :------------------------------------------------------------------------------ |
| `--config`     | Path to a JSON configuration file. If provided, other arguments can be omitted. |
| `--slug`       | Your NationBuilder nation slug (required if not in config).                     |
| `--token`      | Your Developer API Token (required if not in config).                           |
| `--prefixes`   | Space-separated list of tag prefixes to identify tags for deletion.             |
| `--delete-all` | **DANGER:** Delete ALL tags in the nation. Ignores prefixes.                    |
| `--dry-run`    | Simulate deletion without making any changes.                                   |
| `--help`       | Show the help message and exit.                                                 |

**Example:**
Run a simulation using specific credentials and prefixes:

```bash
python nb_tag_cleaner.py --slug mynation --token 12345 --prefixes "Temp:" "Draft:" --dry-run
```
