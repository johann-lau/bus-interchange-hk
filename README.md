# Bus-Interchanges-HK
Bus-Interchanges-HK is a fast Mac GUI program to display bus arrival times in Hong Kong.

## Version
Version: 0.0.1

Updated: 22 September 2023, 09:00 UTC

## Installation
1. Obtain the latest copy of the project:
**If you are viewing this on GitHub**,
Press the green Code button and select "Download ZIP", then unzip the downloaded file.
**If you are viewing this from your local storage**,
you likely already have the project downloaded;
you can still get an updated version by following the steps above.

![Screenshot of how the ZIP file can be downloaded](/screenshots/download.png)

2. Set the permission: Due to the nature of permissions,
you need to enable the execution permission for the program before running.
Right click on the `yt-downloader-mac` folder and select **New Terminal at Folder**.

![Screenshot of how the terminal folder can be opened](/screenshots/permission.png)

![Screenshot of what the terminal looks like](/screenshots/chmod1.png)

3. Type `chmod +x dependencies.command run.command` and press enter.
You can then close the terminal window.

4. Congratulations! You have installed the project and can run it.
Remember - every time you download the ZIP again,
you need to re-enable permissions by following steps 2-3 above.

## Pre-loaded interchange files
This program comes with a few pre-loaded iinterchanges in the ./interchanges directory:

|             Filename             |             Summary             | Contents |
| :------------------------------: | :-----------------------------: | :------: |
| interchanges_cross_harbour.json  | 3 Cross-Harbour Tunnels         | Cross Harbour Tunnel (Hung Hom), Western & Eastern Harbour Crossing
| interchanges_NTW_KLN.json        | Tunnels between New Territories Northwest and Kowloon | Currently Tuen Mun Highway Bus Interchange only. Tai Lam Tunnel to-be-done.

## Running
To run the program, just go into the `bus-interchanges-hk` folder, and double click `run.command`.

1. A terminal window will display a table of interchange files in the ./interchanges directory.
Enter the corresponding number and press enter.

2.

> [!NOTE]
> Do not edit files 


## Troubleshooting

#### chmod: No such file or directory
Please make sure that `dependencies.command` and `run.command` are in the folder, and that you used
"New Terminal at Folder" on the correct folder. Check for typos within the filenames as well.

#### Missing video description
Unfortunately, this may happen to some videos due to an issue with the library `pytube`. There is nothing we can do about this, but be assured as the video title should always be correct.

#### Common fixes
These are some generic items that you should check:

- MacOS (Unfortunately, only MacOS is supported right now, but we plan to add support for other operating systems soon.)
- Latest version of the project (check Step 1 of Installation to obtain the latest version)
- Correct URL entered in textbox
- Stable Internet connection

#### I found a bug that is not listed above! / I want to request a new issue!
Visit the [issue page](https://github.com/johann-lau/yt-downloader-mac/issues) and create a new issue. Please use the default templates provided if possible, and include the `log.log` file if needed. We will process your request as soon as possible.


## Developer
Would you like to contribute? Know someone proficient in Python or Shell scripting? Drop me a message or E-mail me at johannlau8888@gmail.com


## License
This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.