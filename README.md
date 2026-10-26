# Web Application Exercise
A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement
Jobify is a mobile web app that lets job seekers record, track and update every application they send out, keeping all the important information in one place.

## User stories

The check out user stories, see our [project backlog](https://github.com/orgs/software-students-fall2026/projects/8/views/1). 

## Steps necessary to run the software
These steps assume macOS or Linux. On Windows, run every command in WSL or Git Bash, not PowerShell, and use `python` instead of `python3`.

### 1. Check that Python 3.12 is installed

```bash
python3 --version
```

If it prints `Python 3.12.x`, move on. If the command is not found or shows an older version, install Python 3.12:

- **Mac or Windows:** download it from [python.org](https://www.python.org/downloads/)

### 2. Check that Git is installed

```bash
git --version
```

If it prints a version number, move on. If not, install Git:

- **Mac:** `xcode-select --install`
- **Windows:** download it from [git-scm.com](https://git-scm.com/downloads)

### 3. Check that pipenv is installed

```bash
pipenv --version
```

If it prints a version number, move on. If not, install it:

```bash
python3 -m pip install pipenv
```

Then close and reopen your terminal so the `pipenv` command is found.

### 4. Clone the repository

```bash
git clone https://github.com/software-students-fall2026/web-app-exercise-LDJC.git
cd web-app-exercise-LDJC
```

### 5. Install the project's packages

```bash
pipenv install
pipenv shell
```

Your terminal prompt should now start with `(web-app-exercise-LDJC)`.

### 6. Create the `.env` file

Copy the example file:

```bash
cp env.example .env
```

Open `.env` and replace the placeholder values with the real database credentials. Our team's `.env` contents are in our team's Discord channel (leodiajulce222).

### 7. Run the app

```bash
python3 -m flask --app app run --debug
```

Check that the terminal prints `Connected to MongoDB!`, then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

To stop the app, press `Ctrl+C`.

If you see `Address already in use` (port 5000 is often taken by AirPlay on macOS), run the app on another port and open [http://127.0.0.1:5050](http://127.0.0.1:5050) instead:

```bash
python3 -m flask --app app run --debug --port 5050
```

## Task boards

- Link to the [Sprint 1 task board.](https://github.com/orgs/software-students-fall2026/projects/8/views/2)
- Link to the [Sprint 2 task board.](https://github.com/orgs/software-students-fall2026/projects/8/views/3)
