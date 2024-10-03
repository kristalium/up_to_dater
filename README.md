# up_to_dater
Do you make mods and submods for HOI4? Are you tired of evil developers that release updates and break your code? The solution is finally here, and it almost works!

## What?
While it is a good practice to create separate files for your modifications so you don't overwrite original files, sometimes you just have to overwrite something. 
And if something ever changes in the file you overwrite, you will have to manually put your code back in, because who knows what did they update. File POL.txt or POL.txt in a different folder? Line 1001 or 12043?
This ultimately hurts the quality of content, since you are forced to change less in order to keep your mod up to date.

To fix all of that, this script inserts your code into updated file automatically. It takes original file and your modified file, then it compares them, line by line, looking for every difference that they have. 
After comparison everything that was removed or added in the update gets removed or added, and your code gets placed right were it was before the update. All you have to do is mark your lines of code with comments.

Comment your new lines like this:\
`###MOD_ADD1###`   
`something something`\
`###MOD_ADD2###`

Erase lines that you don't want and put this comment where they were:\
`###MOD_DEL###`

Or replace code with whatever you want, by putting these comments around original lines:\
`###MOD_REP1###`   
`something something`\
`###MOD_REP2###`

And your code will stay right were it was.

The only case when it doesn't work is when code around your modifications gets changed too much. 
For example, if you modified country_event.1 giving it some new options, but it got removed from the file completely - script will see that your code is being inserted into the wrong place and will mark the place of failed insertion with ###MOD_FAIL### inside the file, and output file itself will be named as FAILED_OUTPUT.xxx, so you can easily search through your entire mod folder and see what files need your close attention.
So yeah, big updates that change things directly related to you code are still going to mess everything up, but other things might survive, making your life easier.

## Keep in mind! 
This is a half-blind text copy-pasting machine, it is not 100% accurate and can make some unexpected mistakes. Check the output code for problems.

Don't delete your mod files after the script gives you the output. Backups are important. 

Script was tested on HOI4 code - I have no idea if it works for other Paradox games. If it does, well, great.

## How to use
1. Download [Python](https://www.python.org/downloads/), then this script (with a green button that says <code>). If it doesn't work right away try to check if tkinter got installed or not.

2. Now go to your mod and mark all things that you changed in the game files. Instruction for people who like diagrams:

![howto](https://github.com/kristalium/up_to_dater/assets/163107856/23d042b8-44e6-47b5-818b-5150f5be6ecd)

You can do it inside any file - .txt .yml .gui - doesn't matter.

3. Run the script. Select the folders with files. Select original file first, then your file second.

![window](https://github.com/kristalium/up_to_dater/assets/163107856/acf1604d-0f7b-423d-ab8c-95f1a8fb6897)

4. Press the red button.

5. Beep boop.

6. Done. You can get three results.
   First - xxx_FAILED_OUTPUT.xxx Maybe code changed too much, or you placed markers incorrectly, go check the file either way, something is wrong with it.
   Second - xxx_output.xxx That means original file got updated in some way, but the script succesfully inserted your code into it. This is good, but not a guarantee that everythings works fine in the game. Check the code, test in game.
   Third - nothing. If script didn't detect any new content in the original file, you get no output at all. This is the best scenario, since you don't have to check anything.

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
