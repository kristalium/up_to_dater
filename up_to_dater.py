###As one great programmer said: "A genius admires simplicity, an idiot admires complexity."
###And this code was made by an idiot who uses python for the first time in his life.

import re
import os
import threading
import tkinter as tk
from tkinter import filedialog

###Shows that original code changed too much, and attempts to put your code into it will result in bad output.
mod_fail = False 

config_file = os.path.join(os.path.dirname(__file__), 'file_paths.txt')

def read_file(filepath):
    all_file_lines = {}
    try:
        with open(filepath, 'r') as file:
            for idx, line in enumerate(file):
                original_line = line.rstrip('\n') 
                all_file_lines[f"mod_line{idx+1:06d}"] = original_line
        return all_file_lines
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None
        
###Reading files
def process_files(mod_file, submod_file, output_file):
    all_mod_lines_list = read_file(mod_file) ###Dictionary with all of the mod lines.
    all_submod_lines_list = {} ###And with all submod lines.
    try:
        with open(submod_file, 'r') as file:
        
            current_submod_section = "" ###Utility variable to assign lines to variables in this function.
            is_in_submod_section = False
            is_in_replacement_section = False
            submod_section_index = 1
            
            for line in file:
            
                original_line = line.rstrip('\n') 
                if original_line.strip() == "###MOD_ADD1###": ###If there is a line that starts with MOD_ADD1...
                    is_in_submod_section = True              ###...Your mod code was encountered. 
                    current_submod_section += original_line + "\n"
                    continue
                    
                elif original_line.strip() == "###MOD_ADD2###":
                    is_in_submod_section = False             ###And all following code will be included into the single variable, until MOD_ADD2 is found.
                    current_submod_section += original_line + "\n"
                    all_submod_lines_list[f"submod_line{submod_section_index:06d}"] = current_submod_section
                    submod_section_index += 1
                    current_submod_section = ""
                    continue
                    
                elif original_line.strip() == "###MOD_REP1###":
                    is_in_replacement_section = True
                    current_submod_section += original_line + "\n"
                    continue
                    
                elif original_line.strip() == "###MOD_REP2###":
                    is_in_replacement_section = False
                    current_submod_section += original_line + "\n"
                    all_submod_lines_list[f"submod_line{submod_section_index:06d}"] = current_submod_section
                    submod_section_index += 1
                    current_submod_section = ""
                    continue    
                    
                if is_in_submod_section or is_in_replacement_section:
                    current_submod_section += original_line + "\n"
                    
                else:
                    all_submod_lines_list[f"submod_line{submod_section_index:06d}"] = original_line
                    submod_section_index += 1
    except Exception as e:
        print(f"Error reading submod file: {e}")
        return
    
    ###Looks for the markers inside the sequence.
    def contains_marker(line, markers):
        for marker in markers:
            if re.search(re.escape(marker), line):
                return True
        return False
    
    ###This is a bad function. Very bad. And very necessary. It checks if a certain sequence of submod lines exist somewhere in the original code. ! ALL ! of the original code.
    ###Running this is needed to determine how much content was removed or added in the original file after it got updated.
    def find_submod_in_mod_sequence(submod_sequence, all_mod_lines_list, start_index):
        mod_values = list(all_mod_lines_list.values())
        submod_length = len(submod_sequence)
        log_count = 0
        max_log_entries = 10000 ###I used this to debug the code. It gave me a gigabyte sized log file, but whatever... What matters - it probably gives the function a kick in the ass to actually work, otherwise, if this is set to anything lower than 10000, it doesn't. Why? Why.
    
        for i in range(start_index, len(mod_values) - submod_length + 1):
            if [line.strip() for line in mod_values[i:i + submod_length]] == [line.strip() for line in submod_sequence]:
                return True
                
            elif log_count < max_log_entries:
                log_count += 1
                
        if log_count >= max_log_entries:
            print("Too many mismatches, shut up.")
            
        return False
    
    ###Like the previous function, but reversed - this one looks if mod lines exist in submod. Used to determine how much lines did you remove or add to the code.
    ###Also handles situations where markers are too close to each other, which causes some problems finding the proper place to stop the loop.
    def find_mod_in_submod_sequence(mod_sequence, all_submod_lines_list, start_index):
        log_count = 0
        max_log_entries = 10000
        
        for i in range(start_index, end_index):
            ###Getting variables naked because whitespaces ruin checks
            stripped_submod_sequence = [line.strip() for line in submod_values[i:i + lookahead]]
            util_stripped_submod_sequence = [line.strip() for line in submod_values[i:i + util_lookahead]]
            
            ###Check if there is marker in near 2 lines
            if any(contains_marker(line, ["###MOD_ADD1###", "###MOD_DEL###", "###MOD_REP1###"]) for line in util_stripped_submod_sequence) and marker_found == False and markers_in_submod_sequence_one_fail_flag == False:
                return "markers_in_submod_sequence_one"
                
            ###There is none
            elif markers_in_submod_sequence_one_fail_flag == False and marker_found == False:
                return "markers_in_submod_sequence_one_fail"
                
            ###Check if there is a marker in near 6 lines
            elif any(contains_marker(line, ["###MOD_ADD1###", "###MOD_DEL###", "###MOD_REP1###"]) for line in util_stripped_submod_sequence) and marker_found == False and markers_in_submod_sequence_two_fail_flag == False:
                return "markers_in_submod_sequence_two"
                
            ###There is none
            elif markers_in_submod_sequence_two_fail_flag == False and marker_found == False:
                return "markers_in_submod_sequence_two_fail"
                
            ###Both lines can be equal if they are "}" or " ", but this does not mean they are in proper place.
            elif (stripped_submod_sequence == stripped_mod_sequence and all(char in {"", " ", "}"} for char in stripped_mod_sequence)):
                return "markers_second_check"
                
            ###Reverse logic. If previous lines were both "}" or " ", but next ones are not equal, script probably skipped enough same lines and previous lines were actually in proper place.
            elif stripped_submod_sequence != stripped_mod_sequence and markers_second_check_started == True:
                return True
                
            ###Everything is equal without a marker, good.
            elif stripped_submod_sequence == stripped_mod_sequence and marker_found == False:
                return True
                
            ###Everything is equal with a marker, good. Why two checks??? Uh...
            elif stripped_submod_sequence == stripped_mod_sequence and marker_found == True:
                return True
                
            ###Limits the amount of iterations of this loop if marker was found.
            elif marker_found == True and (i > start_index):
                break
                
            ###Limits the amount of iterations of this loop by counting iterations of this loop because why not. Also I used this to create logs.
            if log_count < max_log_entries:
                log_count += 1
        
        ###Limit was reached, but common lines were mot found.
        return False

        if log_count >= max_log_entries:
            print("Too many mismatches, shut up.")
            
###Comparing lines, printing output
    try:
        with open(output_file, 'w') as file:            
            global mod_fail
            sorted_mod_indexes = sorted(all_mod_lines_list.keys())
            sorted_submod_indexes = sorted(all_submod_lines_list.keys())
                        
            new_content_found = False ###Marks that original code changed a lot.
            new_content_end_found = False ###The end of changes was found, both sets of code are in proper spot again.
            
            mod_deletion_started = False
            mod_deletion_completed = False
            
            MOD_REP1lacement_started = False 
            MOD_REP1lacement_completed = False
            
            marker_found = False
            markers_in_submod_sequence_one_fail_flag = False
            markers_in_submod_sequence_two_fail_flag = False
            markers_second_check_started = False
            ###This counts how much times function find_mod_in_submod_sequence failed to find proper start spop when marker was found near.
            fail_counter = 0 
            
            ###Counting how much lines were added or deleted
            mod_line_index_increaser = 0
            mod_line_index_decreaser = 0
            submod_line_index_increaser = 0
            submod_line_index_decreaser = 0
            
            ###Size of sequence of lines that script uses to determine where new content, deletion or replacement functions end.
            ###Set to six because it worked for me, but this is guaranteed to cause bad output in some cases.
            ###The more the number is, the more accurate script finds ends of changes,
            ###but if set to too big of a number there is a chance that sequence does not exist anymore, which will result in failed check.
            lookahead_constant = 6 
            lookahead = lookahead_constant             
            util_lookahead = 2
            
            i = -1
            
            while True:
                i += 1
                ###Asigning index for this iteration
                mod_line_index = sorted_mod_indexes[i + mod_line_index_increaser - mod_line_index_decreaser] if i + mod_line_index_increaser - mod_line_index_decreaser < len(sorted_mod_indexes) else None
                submod_line_index = sorted_submod_indexes[i + submod_line_index_increaser - submod_line_index_decreaser] if i + submod_line_index_increaser - submod_line_index_decreaser < len(sorted_submod_indexes) else None
                
                ###Stops the loop if lines are empty. Do not touch.
                if mod_line_index is None and (not "###MOD_ADD1###" in next_submod_line and not "###MOD_DEL###" in next_submod_line and not "###MOD_REP1###" in next_submod_line):
                    break 
                
                ###Get the line from the list based on it's index
                current_mod_line = all_mod_lines_list.get(mod_line_index, "")
                current_submod_line = all_submod_lines_list.get(submod_line_index, "")
                
                ###Getting indexes and values of next lines. This is needed to set new_content_found to true or false later on.
                next_mod_line_index = sorted_mod_indexes[i + 1 + mod_line_index_increaser - mod_line_index_decreaser] if i + 1 + mod_line_index_increaser - mod_line_index_decreaser < len(sorted_mod_indexes) else None 
                next_submod_line_index = sorted_submod_indexes[i + 1 + submod_line_index_increaser - submod_line_index_decreaser] if i + 1 + submod_line_index_increaser - submod_line_index_decreaser < len(sorted_submod_indexes) else None
                next_mod_line = all_mod_lines_list.get(next_mod_line_index, "")
                next_submod_line = all_submod_lines_list.get(next_submod_line_index, "")
                
                ###Detecting new content
                if new_content_found == False and mod_deletion_started == False and MOD_REP1lacement_started == False and current_mod_line.strip() != current_submod_line.strip() and next_mod_line.strip() != next_submod_line.strip() and (not "###MOD_ADD1###" in current_submod_line and not "###MOD_DEL###" in current_submod_line and not "###MOD_REP1###" in current_submod_line):
                   new_content_found = True
                   new_content_end_found = False
                   file.write(current_mod_line + "\n") 
                
                ###Detecting new content and markers in the same time, which means something is very wrong with the code.
                elif new_content_found == True and ("###MOD_ADD1###" in current_submod_line or "###MOD_DEL###" in current_submod_line or "###MOD_REP1###" in current_submod_line):
                    mod_fail = True
                    file.write("###MOD_FAIL###\n")
                    file.write(current_submod_line)
                    file.write("###MOD_FAIL###\n")
                    submod_line_index_increaser += 2
                    
                    ###Deletion marker found.
                elif mod_deletion_started == False and "###MOD_DEL###" in current_submod_line:
                    file.write(current_submod_line + "\n")                    
                    mod_deletion_started = True
                    mod_deletion_completed = False                    
                    submod_line_index_increaser += 1
                
                    ###Replacement marker found.
                elif MOD_REP1lacement_started == False and "###MOD_REP1###" in current_submod_line:
                    file.write(current_submod_line)
                    MOD_REP1lacement_started = True
                    MOD_REP1lacement_completed = False                                        
                    mod_line_index_decreaser += 1
                    submod_line_index_increaser +=1    
                
                ###Printing before the closing brace and before the opening brace, because it is bad idea to it the other way around.
                if ("}" in current_mod_line or "{" in current_mod_line) and "###MOD_ADD1###" in current_submod_line:
                    file.write(current_submod_line)
                    file.write(current_mod_line + "\n")                    
                    submod_line_index_increaser += 1
                
                ###Mod content remover and replacer. 
                ###It looks that bad because it is a pretty complicated task to keep track of all changes that might happen to the code simultaneously.
                    ###Is there any lines to print after delition/replacement is over?
                elif (mod_deletion_started == True and mod_deletion_completed == False) or (MOD_REP1lacement_started == True and MOD_REP1lacement_completed == False):
                                     
                    submod_values = list(all_submod_lines_list.values()) ###Get all lines from dictionary with submod values.
                    mod_sequence = [all_mod_lines_list.get(sorted_mod_indexes[i + 1 + mod_line_index_increaser - mod_line_index_decreaser + k], "") for k in range(lookahead)] ###Get a sequence of lines with the size of lookahead
                    stripped_mod_sequence = [line.strip() for line in mod_sequence] ###Clean mod sequence, need to unify this with previous var, no point in creating two of them.
                    
                    end_index = len(submod_values) - lookahead + 1 
                    
                    ###Creating a separate sequence with the size of util_lookahead to work in short distances
                    util_start_index = i + submod_line_index_increaser - submod_line_index_decreaser
                    util_mod_sequence = [all_mod_lines_list.get(sorted_mod_indexes[i + 1 + mod_line_index_increaser - mod_line_index_decreaser + k], "") for k in range(util_lookahead)]
                    util_stripped_mod_sequence = [line.strip() for line in util_mod_sequence]
                    
                    function_result = find_mod_in_submod_sequence(mod_sequence, all_submod_lines_list, util_start_index)
                    ###New marker is super close. Let's check less carefully.
                    if function_result == "markers_in_submod_sequence_one":                                                                                                                                                                                                                                                                     
                        marker_found = True
                        lookahead = 1
                        submod_line_index_decreaser += 1
                        
                    ###No markers super close.    
                    elif function_result == "markers_in_submod_sequence_one_fail" and markers_in_submod_sequence_one_fail_flag == False:
                        mod_line_index_decreaser += 1
                        submod_line_index_decreaser += 1
                        markers_in_submod_sequence_one_fail_flag = True
                        util_lookahead = lookahead
                        
                    ###New marker is near. Let's check less carefully.                                                                                                                                                 
                    elif function_result == "markers_in_submod_sequence_two":                                                                                                                       
                        submod_line_index_decreaser += 1
                        marker_found = True
                        lookahead = 2
                        
                    ###New marker is not anywhere near at all.                                                                                                                                                 
                    elif function_result == "markers_in_submod_sequence_two_fail" and markers_in_submod_sequence_two_fail_flag == False:                        
                        mod_line_index_decreaser += 1
                        submod_line_index_decreaser += 1
                        markers_in_submod_sequence_two_fail_flag = True
                        
                    ###Found the lines, but they are all spaces or braces, which might be false positive. Checking next lines.
                    elif function_result == "markers_second_check":
                        submod_line_index_decreaser += 1
                        markers_second_check_started = True
                        
                    ###Doesn't look that way, checking some more.
                    elif function_result == False:                                                                                                                                            
                        submod_line_index_decreaser += 1
                     
                    ###Found the lines. The delition/replacement is over, continuing as usual.
                    elif function_result == True and markers_second_check_started == True:
                        file.write(current_mod_line + "\n")
                        mod_deletion_started = False
                        mod_deletion_completed = False
                        MOD_REP1lacement_started = False
                        MOD_REP1lacement_completed = False
                        marker_found = False
                        markers_in_submod_sequence_one_fail_flag = False
                        markers_in_submod_sequence_two_fail_flag = False
                        markers_second_check_started = False
                        lookahead = lookahead_constant
                        util_lookahead = 2
                        
                    ###Found the lines. The delition/replacement is over, continuing as usual.
                    elif function_result == True:
                        mod_deletion_started = False
                        mod_deletion_completed = False
                        MOD_REP1lacement_started = False
                        MOD_REP1lacement_completed = False
                        marker_found = False
                        markers_in_submod_sequence_one_fail_flag = False
                        markers_in_submod_sequence_two_fail_flag = False
                        markers_second_check_started = False
                        submod_line_index_decreaser += 1
                        lookahead = lookahead_constant
                        util_lookahead = 2
                ###Mod content remover end        
                    
                    ###Lines are not equal. ###MOD_ADD1### detected, printing mod code and then your code.
                elif current_mod_line.strip() != current_submod_line.strip() and "###MOD_ADD1###" in current_submod_line and not new_content_found == True:
                    file.write(current_mod_line + "\n")
                    file.write(current_submod_line)
                    submod_line_index_increaser +=1                    
                
                ###New content printer
                    ###Next lines are equal, but they are both spaces or braces. Not accurate enough to be sure, let's check some more.
                elif new_content_found == True and new_content_end_found == False and ((next_mod_line.strip() == "" and next_submod_line.strip() == "") or (next_mod_line.strip() == "}" and next_submod_line.strip() == "}")):
                    file.write(current_mod_line + "\n")
                    mod_line_index_decreaser += 1
                    submod_line_index_increaser += 1
                    
                    ###Next lines are equal, but they are both spaces or braces. Not accurate enough to be sure, let's look for other end.
                elif new_content_found == True and new_content_end_found == True and ((next_mod_line.strip() == "" and next_submod_line.strip() == "") or (next_mod_line.strip() == "}" and next_submod_line.strip() == "}")):                                       
                    file.write(current_mod_line + "\n")      
                    
                    ###Printing more code from the mod until we find where it ends. Also, do those submod lines even exist inside the mod?
                elif new_content_found == True and new_content_end_found == False and next_mod_line.strip() != next_submod_line.strip():
                    ###Getting submod sequence, with a check that prevents it from trying to grab non-existing variables.
                    submod_sequence = [all_submod_lines_list.get(sorted_submod_indexes[i + 1 + submod_line_index_increaser - submod_line_index_decreaser + k], "") for k in range(lookahead) if i + 1 + submod_line_index_increaser - submod_line_index_decreaser + k < len(sorted_submod_indexes)]
                    
                    ###They do not, probably got removed. Let's try checking other lines to find where everything matches again
                    if not find_submod_in_mod_sequence(submod_sequence, all_mod_lines_list, i):
                        mod_line_index_decreaser += 1
                        
                    ###They do. Let's wait for them to appear then.    
                    else:
                        submod_line_index_decreaser += 1
                        new_content_end_found = True
                        
                    ###Next lines are equal, and they are not spaces or braces. New mod code is over.    
                elif new_content_found == True and next_mod_line.strip() == next_submod_line.strip():
                    file.write(current_mod_line + "\n")
                    new_content_found = False 
                
                    ###Printing mod lines, waiting for equal submod lines.
                elif new_content_found == True and new_content_end_found == True:
                    submod_line_index_decreaser += 1
                    file.write(current_mod_line + "\n")
                ###New code printer end
                
                ###This is for the cases when only one line of code in the mod was changed after update, not a whole block.
                elif new_content_found == False and current_mod_line.strip() != current_submod_line.strip() and next_mod_line.strip() == next_submod_line.strip():               
                    file.write(current_mod_line + "\n")
                    
                ###Lines are the same. Keeping the code from the original mod    
                elif current_mod_line.strip() == current_submod_line.strip():
                    file.write(current_mod_line + "\n")  
                
                else:
                    print("Unexpected case, kristalium fucked up.")
        
        if mod_fail == True:
            failed_output_file = os.path.splitext(submod_file)[0] + "_FAILED_OUTPUT" + os.path.splitext(submod_file)[1]
            if os.path.exists(failed_output_file):
                os.remove(failed_output_file)
            os.rename(output_file, failed_output_file)
            mod_fail = False
            
    except Exception as e:
        print(f"Error writing to output file: {e}")

def main():
    try:
        with open(config_file, 'r') as file:
        
            for line in file:
                line = line.strip()
                
                if not line:
                    continue
                    
                paths = line.split(',')
                file_paths = {}
                
                for path in paths:
                    key, value = map(str.strip, path.split('='))
                    file_paths[key] = value
                    
                mod_file = file_paths.get('mod_file')
                submod_file = file_paths.get('submod_file')
                
                if mod_file and submod_file:
                    output_file = os.path.splitext(submod_file)[0] + "_output" + os.path.splitext(submod_file)[1]
                    process_files(mod_file, submod_file, output_file)
                    
                else:
                    print(f"Invalid configuration line: {line}")
                    
    except Exception as e:
        print(f"Error reading config file: {e}")

#####THE INTERFACE#####
###Add your stuff
def add_pair():
    mod_path = filedialog.askopenfilename()
    if mod_path:
        submod_path = filedialog.askopenfilename()
        if submod_path:
            with open('file_paths.txt', 'a') as f:
                f.write(f"mod_file={mod_path},submod_file={submod_path}\n")
            refresh_listbox()

###Delete your stuff (not the files themself, the paths to files)
def delete_pair():
    selected_index = listbox.curselection()
    if selected_index:
        with open('file_paths.txt', 'r') as f:
            lines = f.readlines()
        with open('file_paths.txt', 'w') as f:
            for i, line in enumerate(lines):
                if i != selected_index[0]:
                    f.write(line)
        refresh_listbox()

###Refresh
def refresh_listbox():
    listbox.delete(0, tk.END)
    with open('file_paths.txt', 'r') as f:
        for line in f:
            mod_path = line.split(",")[0].split(":")[1].strip()
            submod_path = line.split(",")[1].split(":")[1].strip()
            mod_name = os.path.basename(mod_path)
            submod_name = os.path.basename(submod_path)
            listbox.insert(tk.END, f"Original file: {mod_name}, Your file: {submod_name}")
            status_label.config(text="")

###RUN
def run_script():
    selected_index = listbox.curselection()
    
    if not selected_index:
        selected_index = (0,)
        
    if selected_index:
        with open('file_paths.txt', 'r') as f:
            lines = f.readlines()
            if len(lines) > 0:
                mod_path = lines[selected_index[0]].split(",")[0].split(":")[1].strip()
                submod_path = lines[selected_index[0]].split(",")[1].split(":")[1].strip()
                
                status_label.config(text="Running script...")
                
                def script_thread():
                    try:
                        main()
                        status_label.config(text="Script executed successfully. Or not.")
                    except Exception as e:
                        status_label.config(text=f"Error: {str(e)}")
                
                thread = threading.Thread(target=script_thread)
                thread.start()
 
            else:
                status_label.config(text="No paths available to run.")
            
###Title
root = tk.Tk()
root.title("Up_to_dater")

###Instructions
root.configure(bg='black')

label = tk.Label(root, text="Press 'Add Pair', select the original file, then your file.", bg='black', fg='white')
label.pack(pady=10)

frame = tk.Frame(root, bg='black')
frame.pack(padx=10, pady=10)

listbox = tk.Listbox(frame, width=100, height=10, bg='black', fg='white', selectbackground='gray', selectforeground='black')
listbox.pack(side=tk.LEFT, fill=tk.BOTH)

scrollbar = tk.Scrollbar(frame, orient="vertical")
scrollbar.config(command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)

button_frame = tk.Frame(root, bg='black')
button_frame.pack(pady=10)

add_button = tk.Button(button_frame, text="Add Pair", command=add_pair, bg='white', fg='black')
add_button.grid(row=0, column=0, padx=5, pady=5)

refresh_button = tk.Button(button_frame, text="Refresh List", command=refresh_listbox, bg='white', fg='black')
refresh_button.grid(row=0, column=1, padx=5, pady=5)

delete_button = tk.Button(button_frame, text="Delete Pair", command=delete_pair, bg='white', fg='black')
delete_button.grid(row=0, column=2, padx=5, pady=5)

run_button = tk.Button(button_frame, text="Run Script", command=run_script, bg='red', fg='black')
run_button.grid(row=1, column=1, pady=10)

status_label = tk.Label(root, text="", bg='black', fg='white')
status_label.pack(pady=10)

refresh_listbox()

root.mainloop()