# Radare2 reversing tool
## Reverse
- main control script: `run_reverse.sh`
- usage
    ```
    $ bash run_reverse.sh

    # Run the script with
    #   $ bash run_reverse.sh [-h] [-d <directory>] [-f <file>] [-l <file>]

    #     -h    Show help
    #     -d    The directory with binaries to be reversed
    #     -f    The file to be reversed
    #     -l    The file with a list of files to be reversed
    ```

- configuration: `reverse.conf`

    | Var         | Desc                                  | Option                                   |
    | ---         | ---                                   | ---                                      |
    | MAIN_SCRIPT | location to the main reversing script |                                          |
    | LOG_DIR     | directory to save logs                |                                          |
    | FCG_DIR     | directory to save fcg files           |                                          |
    | WORKERS     | maximum number of processes           |                                          |
    | TIMEOUT     | timeout in seconds                    |                                          |
    | STATE_LIST  | list of finish paths and their states |                                          |
    | SKIP        | skip analyzed files                   | 0) do not skip<br>1) skip all            |
    | SHUFFLE     | analyze in random order               | 0) in sorted order<br>1) in random order |

- state: `STATE_LIST`
    - format: `<file path>,<state>`

        | State | Desc                                       |
        | ---   | ---                                        |
        | 0     | Success                                    |
        | 1     | Error while reversing                      |
        | 124   | Timeout (SIGTERM)                          |
        | 137   | Killed (SIGKILL), only when Timeout failed |

- example
    1. start run
        ```
        # terminal 1
        bash run_reverse.sh -d mybinaries/ > /tmp/run.log
        ```
    2. monitor progress
        ```
        # terminal 2
        tail -f run.log
        ```
    3. terminate
        ```
        # terminal 1
        <CTRL + C>  # and wait for the running processes to finish
        ```