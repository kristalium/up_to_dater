# up_to_dater
Do you make mods and submods for HOI4? Are you tired of evil developers that release updates and break your code? The solution is finally here, and it almost works!

## What?
While it is a good practice to create separate files for your modifications so you don't overwrite original files, sometimes you just have to overwrite something. And when you do that, every update has a chance to break your code. 
Very sad. And takes some work to fix it. Or a lot. 
And ultimately it hurts the quality of content, because having to redo your work is really disincentivizing and forces you to do less.

To fix all of that, this script inserts your modifications into updated code automatically. It takes original code and your modified code, then it compares them, line by line, looking for every difference that they have. Everything that was removed or added in the update gets removed or added, but your code gets placed right were it was before the update. All you have to do is mark your lines of code with comments.

Comment your new lines like this:\
`###MOD_ADD1###`   
`something something`\
`###MOD_ADD2###`

Erase lines that you don't want and put this comment where they were:\
`###MOD_DEL###`

Or replace code with whatever you want, by putting these comments around original lines:\
`###MOD_REP1###`   
`northing nothing`\
`###MOD_REP2###`

And your code will stay right were it was.

The only case when it doesn't work is when code around your modifications gets changed too much. 
For example, if you modified an event news.1.a, but it got removed from the file completely, script will mark the place of failed insertion with ###MOD_FAIL###, and name output file as FAILED_OUTPUT.xxx
So yeah, big updates still going to mess everything up, but maybe something will survive, making your life easier.

## Keep in mind! 
This is a half-blind text copy-pasting machine, it is not 100% accurate and can make some unexpected mistakes. Check the output code for problems.

Don't delete your mod files after the script gives you the output. Backups are important. 

Script was tested on HOI4 code - I have no idea if it works for other Paradox games. If it does, well, great.

## How to use
1. Download [Python](https://www.python.org/downloads/), then this script. If it doesn't work right away try to check if tkinter got installed or not.

2. Mark all things that you changed in the code with the markers. Instruction for people who like diagrams:

![Диаграмма без названия](https://github.com/kristalium/up_to_dater/assets/163107856/299d75ad-283c-4124-8598-391bfb9faf03)

3. Run the script, select the folders with files. Original file first, your file second.

![image](https://github.com/kristalium/up_to_dater/assets/163107856/55a16a58-c6ad-4aa9-8f22-5239d9985051)

4. Press the red button.

5. Beep boop.

6. Done, output files will appear in the folder with your mod files. Check your code, test your code. Chances are - it works.

## Known issues

#### Do not write new markers right after ###MOD_DEL### or ###MOD_REP1### like this:
`###MOD_DEL###`\
`###MOD_ADD1###`\
Just don't, I don't want to fix that. ###MOD_REP1### combines both addition and deletion, so use it instead of multiple markers. 

#### This kind of code: 
`trigger = { NOT = { original_tag = SOV ###MOD_ADD1### TAG = POL ###MOD_ADD2### TAG = GER } }`

Will never work, script will not recognise this. And even if it would print this, marker ###ADD_MOD### just comments out everything after first #, breaking the code.
Still, some people have a habit of writing code in a single line.

To make your modification appear as a single line (why?) mark it this way:\
`###REP_MOD1###`\
`trigger = { NOT = { original_tag = SOV TAG = POL TAG = GER } }`\
`###REP_MOD2###` 

It is still not perfect, because if anything changes inside the braces you will never know, the script will replace original line with your code not even checking anything.

Best way to fix this will be redacting your submod code to something like this, if possible:\
`trigger = { NOT = { original_tag = SOV TAG = GER } }`\
`###MOD_ADD1###`\
`trigger = {`\
`TAG = POL`\
`}`\
`###MOD_ADD2###`

#### If original code changed after your ###MOD_DEL### or ###MOD_REP1### markers, output will likely be broken.
Really broken. It is pretty hard to even detect how exactly it will break, so I decided not to bother.
