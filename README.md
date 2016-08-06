Guild Wars 2 multiaccount launcher and multiboxer.
Requires administrator mode.
Multiboxing works by closing the "AN-Mutex-Window-Guild Wars 2" handle of
    each game instance and making Local.dat a symbolic link to the .dat
    file connected to the intended account.
Script stores all variables using JSON format in a file named data.json
    which is located in the same directory as the script.

Variables:
- handle: path to handle.exe file
    https://technet.microsoft.com/en-us/sysinternals/handle.aspx
- localPath: the path to the directory where the Local.dat file is located
    default: "%AppData%\Guild Wars 2"
- exePath: path to the Guild Wars 2 executable file
    default: "%ProgramFiles%\Guild Wars 2\Gw2-64.exe"
- params: Guild Wars 2 launch parameters for single instance
    https://wiki.guildwars2.com/wiki/Command_line_arguments
- multiparams: Guild Wars 2 launch parameters for multibox launch
    "-shareArchive" is added automatically