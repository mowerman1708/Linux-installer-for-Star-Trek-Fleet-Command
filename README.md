# Linux-installer-for-Star-Trek-Fleet-Command
This is a work in progress! Use at your own risk.

This is a project I did to install DCS World on GNU/Linux systems without the need for Lutris or Steam.
The script will download the current wine version and DCS World install program. Then it will create a wine 
prefix for the game with a name of your choice if you would like or just create an empty directory and select
that.If you type in a directory you will have to hit OK twice?
The program has an animated label to show when it is working. It does take a few minutes for the downloads
and the prefix creation.
Lastly we start the DCS World install program. If you have ever installed DCS World then you know it takes
a long time to download. The site seems to be capped at 11 MB/s. But anyway 6 1/2 hrs download in my testing.
Last test 8/23 12:30am estd. Size of 218 GB @ 11.5 MB/s with only the Caucus map. It's the source nothing to be
done about it on this side.
The installation will create desktop icons for your use, just follow the prompts and accept the defaults and
remember the installation is in a folder made to resemble Windows drive layout. I haven't actually had the program
run yet but think it may have been in the prefix creation, which is being refined currently. It does launch the
updater but crashes hard before getting a login prompt.
I have another installer for Star Trek Fleet Command that works well. Only problems I run into is closing the program, that normally results in killing the process. Thinking that may be a wine thing? STFC won't shutdown from Lutris either. I Don't generally use Steam but have a nice working copy of Falcon BMS on Linux also. That requires a copy of the old Falcon 4 which is available through Steam but you just needs it for the BMS install progam to detect. The install I am using is through Lutris though. I find that most windows program perform just as well on Linux, just a bit more work to setup than Windows easy installers. Maybe another project some day?
