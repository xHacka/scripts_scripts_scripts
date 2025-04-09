# Utility Scripts

This project provides a collection of utility scripts that can be easily run from CMD or PowerShell. By adding the `run` directory to your *User Environment* PATH variable, all scripts become accessible from anywhere in your terminal.

## Project Structure

```
Root
│   .gitignore
│   generate.cmd
│   README.md
│   
├───draft
│       script_name_in_draft.py
│       
├───run
│       script_name.cmd
│       
└───src
        script_name.py
```

### Directory Purpose

- **src**: Contains production-ready scripts
- **run**: Contains generated command files for executing scripts
- **draft**: Storage for scripts under development

## Getting Started

1. Clone this repository
2. Add the `run` directory to your PATH environment variable
3. Create Python scripts in the `src` directory
4. Run `.\generate.cmd` to generate command files
5. Access any script directly from your command line by typing its name

## Development Workflow

1. Create or modify a Python script in `src` directory
2. Run `.\generate.cmd` to update command files
3. Your script is now available as `script_name.cmd` from any terminal
