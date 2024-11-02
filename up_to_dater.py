import re
import os
import sys
import threading
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QInputDialog,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QFileDialog,
    QScrollArea,
    QFrame,
    QListWidgetItem
)
from PyQt5.QtCore import Qt

###Shows that original code changed too much, and attempts to put your code into it will result in bad output.
mod_fail = False 

###80MB limit on output file size to prevent scary things
file_size_limit = 80 * 1024 * 1024 

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
        max_log_entries = 60
        
        for i in range(start_index, end_index):
            ###Getting variables naked because whitespaces ruin checks
            stripped_submod_sequence = [line.strip() for line in submod_values[i:i + lookahead]]
            util_stripped_submod_sequence = [line.strip() for line in submod_values[i:i + util_lookahead]]
            
            ###Check if there is marker in near 2 lines
            if any(contains_marker(line, ["###MOD_ADD1###", "###MOD_DEL###", "###MOD_REP1###"]) for line in util_stripped_submod_sequence) and marker_found == False and markers_in_submod_sequence_one_fail_flag == False:
                print(f"Marker found at position {i} with util_lookahead {util_lookahead}: stripped submod values {util_stripped_submod_sequence} vs mod sequence {util_stripped_mod_sequence}")
                return "markers_in_submod_sequence_one"
                
            ###There is none
            elif markers_in_submod_sequence_one_fail_flag == False and marker_found == False:
                print(f"No marker found at position {i} with util_lookahead {util_lookahead}: stripped submod values {util_stripped_submod_sequence} vs mod sequence {util_stripped_mod_sequence}")
                return "markers_in_submod_sequence_one_fail"
                
            ###Check if there is a marker in near 6 lines
            elif any(contains_marker(line, ["###MOD_ADD1###", "###MOD_DEL###", "###MOD_REP1###"]) for line in util_stripped_submod_sequence) and marker_found == False and markers_in_submod_sequence_two_fail_flag == False:
                print(f"Marker found at position {i} with util_lookahead {util_lookahead}: stripped submod values {util_stripped_submod_sequence} vs mod sequence {util_stripped_mod_sequence}")
                return "markers_in_submod_sequence_two"
                
            ###There is none
            elif markers_in_submod_sequence_two_fail_flag == False and marker_found == False:
                return "markers_in_submod_sequence_two_fail"
                
            ###Both lines can be equal if they are "}" or " ", but this does not mean they are in proper place.
            elif (stripped_submod_sequence == stripped_mod_sequence and all(char in {"", " ", "}"} for char in stripped_mod_sequence)):
                print(f"Not the best match found at position {i} with lookahead {lookahead}: stripped submod values {stripped_submod_sequence} vs mod sequence {stripped_mod_sequence}")
                return "markers_second_check"
                
            ###Reverse logic. If previous lines were both "}" or " ", but next ones are not equal, script probably skipped enough same lines and previous lines were actually in proper place.
            elif stripped_submod_sequence != stripped_mod_sequence and markers_second_check_started == True:
                print(f"Confirming missmatch found at position {i} with lookahead {lookahead}: stripped submod values {stripped_submod_sequence} vs mod sequence {stripped_mod_sequence}")
                return True
                
            ###Everything is equal without a marker, good.
            elif stripped_submod_sequence == stripped_mod_sequence and marker_found == False:
                print(f"Match found at position {i} with lookahead {lookahead}: stripped submod values {stripped_submod_sequence} vs mod sequence {stripped_mod_sequence}")
                return True
                
            ###Everything is equal with a marker, good.
            elif stripped_submod_sequence == stripped_mod_sequence and marker_found == True:
                print(f"Match found at position {i} with lookahead {lookahead}: stripped submod values {stripped_submod_sequence} vs mod sequence {stripped_mod_sequence}")
                return True
                
            ###Limits the amount of iterations of this loop if marker was found.
            elif marker_found == True and (i > start_index):
                print(f"Breakdance! i - {i} start_index - {start_index} log_count - {log_count}")
                break
                
            ###Limits the amount of iterations of this loop by counting iterations of this loop because why not. Also I used this to create logs.
            if log_count < max_log_entries:
                log_count += 1
                print(f"Mismatch found at position {i} with lookahead {lookahead}: stripped submod values {stripped_submod_sequence} vs mod sequence {stripped_mod_sequence}")
        
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
            constant_new_content_found = False ###If still false after whole code is checked, nothing new was added, meaning that there is no need to generate output file. Cannot be set to False again.
            
            mod_deletion_started = False
            mod_deletion_completed = False
            
            mod_replacement_started = False 
            mod_replacement_completed = False
            
            marker_found = False
            markers_in_submod_sequence_one_fail_flag = False
            markers_in_submod_sequence_two_fail_flag = False
            markers_second_check_started = False
            
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
                
                ###Stops the loop if lines are empty. Do not touch, this is break pedal
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
                
                print(f"\nMod Variable {mod_line_index}: {current_mod_line.strip()}")
                print(f"Submod Variable {submod_line_index}: {current_submod_line.strip()}")
                print(f"Next Mod Variable {next_mod_line_index}: {next_mod_line.strip()}")
                print(f"Next Submod Variable {next_submod_line_index}: {next_submod_line.strip()}")
                
                ###Detecting new content
                if new_content_found == False and mod_deletion_started == False and mod_replacement_started == False and current_mod_line.strip() != current_submod_line.strip() and next_mod_line.strip() != next_submod_line.strip() and (not "###MOD_ADD1###" in current_submod_line and not "###MOD_DEL###" in current_submod_line and not "###MOD_REP1###" in current_submod_line and not submod_line_index is None):
                   new_content_found = True
                   new_content_end_found = False
                   constant_new_content_found = True
                   file.write(current_mod_line + "\n") 
                
                ###Detecting new content and markers in the same time, which means something is very wrong with the code.
                elif new_content_found == True and ("###MOD_ADD1###" in current_submod_line or "###MOD_DEL###" in current_submod_line or "###MOD_REP1###" in current_submod_line):
                    mod_fail = True
                    file.write("###MOD_FAIL###\n")
                    file.write(current_submod_line)
                    file.write("###MOD_FAIL###\n")
                    
                    submod_line_index_increaser += 2
                    continue
                
                elif mod_deletion_started == False and "###MOD_DEL###" in current_submod_line:
                    file.write(current_submod_line + "\n")
                    
                    mod_deletion_started = True
                    mod_deletion_completed = False                    
                    submod_line_index_increaser += 1
                
                elif mod_replacement_started == False and "###MOD_REP1###" in current_submod_line:
                    file.write(current_submod_line)
                    mod_replacement_started = True
                    mod_replacement_completed = False                    
                    
                    mod_line_index_decreaser += 1
                    submod_line_index_increaser +=1    
                
                ###Printing before the closing brace and before the opening brace, because it is bad idea to it the other way around.
                if ("}" in current_mod_line or "{" in current_mod_line) and "###MOD_ADD1###" in current_submod_line:
                    file.write(current_submod_line)
                    file.write(current_mod_line + "\n")
                    
                    submod_line_index_increaser += 1
                
                ######################################
                ###Mod content remover and replacer###
                ######################################
                ###It looks that bad because it is a pretty complicated task to keep track of all changes that might happen to the code simultaneously.
                elif (mod_deletion_started == True and mod_deletion_completed == False) or (mod_replacement_started == True and mod_replacement_completed == False):
                                     
                    submod_values = list(all_submod_lines_list.values()) ###Get all lines from dictionary with submod values.
                    mod_sequence = [all_mod_lines_list.get(sorted_mod_indexes[i + 1 + mod_line_index_increaser - mod_line_index_decreaser + k], "") for k in range(lookahead)] ###Get a sequence of lines with the size of lookahead
                    stripped_mod_sequence = [line.strip() for line in mod_sequence] ###Clean mod sequence, need to unify this with previous var, no point in creating two of them.
                    
                    end_index = len(submod_values) - lookahead + 1 
                    
                    ###Creating a separate sequence with the size of util_lookahead to work in short distances
                    util_start_index = i + submod_line_index_increaser - submod_line_index_decreaser
                    util_mod_sequence = [all_mod_lines_list.get(sorted_mod_indexes[i + 1 + mod_line_index_increaser - mod_line_index_decreaser + k], "") for k in range(util_lookahead)]
                    util_stripped_mod_sequence = [line.strip() for line in util_mod_sequence]
                    
                    function_result = find_mod_in_submod_sequence(mod_sequence, all_submod_lines_list, util_start_index)
                    if function_result == "markers_in_submod_sequence_one":                                                                                                                                                                                                                                                                      
                        marker_found = True
                        lookahead = 1
                        
                        submod_line_index_decreaser += 1
                        
                    elif function_result == "markers_in_submod_sequence_one_fail" and markers_in_submod_sequence_one_fail_flag == False:
                        
                        mod_line_index_decreaser += 1
                        submod_line_index_decreaser += 1
                        markers_in_submod_sequence_one_fail_flag = True
                        util_lookahead = lookahead
                        
                    elif function_result == "markers_in_submod_sequence_two":                                                                                                                                                                                                                                                                       
                        
                        submod_line_index_decreaser += 1
                        marker_found = True
                        lookahead = 2    
                        
                    elif function_result == "markers_in_submod_sequence_two_fail" and markers_in_submod_sequence_two_fail_flag == False:                                                                                                                                             
                        
                        mod_line_index_decreaser += 1
                        submod_line_index_decreaser += 1
                        markers_in_submod_sequence_two_fail_flag = True
                    
                    elif function_result == "markers_second_check":
                        submod_line_index_decreaser += 1
                        markers_second_check_started = True
                        
                    elif function_result == False:                                                                                                                                         
                        submod_line_index_decreaser += 1
                     
                    elif function_result == True and markers_second_check_started == True:
                        file.write(current_mod_line + "\n")

                        mod_deletion_started = False
                        mod_deletion_completed = False
                        mod_replacement_started = False
                        mod_replacement_completed = False
                        marker_found = False
                        markers_in_submod_sequence_one_fail_flag = False
                        markers_in_submod_sequence_two_fail_flag = False
                        markers_second_check_started = False
                        lookahead = lookahead_constant
                        util_lookahead = 2
                     
                    elif function_result == True:
                        
                        mod_deletion_started = False
                        mod_deletion_completed = False
                        mod_replacement_started = False
                        mod_replacement_completed = False
                        marker_found = False
                        markers_in_submod_sequence_one_fail_flag = False
                        markers_in_submod_sequence_two_fail_flag = False
                        markers_second_check_started = False
                        submod_line_index_decreaser += 1
                        lookahead = lookahead_constant
                        util_lookahead = 2
                #############################        
                ###Mod content remover end###        
                #############################
                
                elif current_mod_line.strip() != current_submod_line.strip() and "###MOD_ADD1###" in current_submod_line and not new_content_found == True:
                    file.write(current_mod_line + "\n")
                    file.write(current_submod_line)
                    
                    submod_line_index_increaser +=1                    
                
                #########################
                ###New content printer###
                #########################
                elif new_content_found == True and new_content_end_found == False and next_submod_line_index is None:
                    file.write(current_mod_line + "\n")
                    new_content_found = False 
                    
                elif new_content_found == True and new_content_end_found == False and ((next_mod_line.strip() == "" and next_submod_line.strip() == "") or (next_mod_line.strip() == "}" and next_submod_line.strip() == "}")): ### current_submod_line and current_mod_line can have a common line if they are both " " or "}", 
                                                                                                                                                                                                                                ### but this usually doesn't mean that script found right code lines, there are a lot of spaces and braces.
                    mod_line_index_decreaser += 1
                    submod_line_index_increaser += 1
                    
                elif new_content_found == True and new_content_end_found == True and ((next_mod_line.strip() == "" and next_submod_line.strip() == "") or (next_mod_line.strip() == "}" and next_submod_line.strip() == "}")):                                             
                    file.write(current_mod_line + "\n")      
                
                elif new_content_found == True and new_content_end_found == False and next_mod_line.strip() != next_submod_line.strip():
                    ###Getting submod sequence, with a check that prevents it from trying to grab non-existing variables.
                    submod_sequence = [all_submod_lines_list.get(sorted_submod_indexes[i + 1 + submod_line_index_increaser - submod_line_index_decreaser + k], "") for k in range(lookahead) if i + 1 + submod_line_index_increaser - submod_line_index_decreaser + k < len(sorted_submod_indexes)]
                    if not find_submod_in_mod_sequence(submod_sequence, all_mod_lines_list, i):

                        mod_line_index_decreaser += 1
                    else:
                        submod_line_index_decreaser += 1
                        new_content_end_found = True
                        
                elif new_content_found == True and next_mod_line.strip() == next_submod_line.strip():
                    file.write(current_mod_line + "\n")
                    new_content_found = False 
                
                elif new_content_found == True and new_content_end_found == True:
                    
                    submod_line_index_decreaser += 1
                    file.write(current_mod_line + "\n")
                ##########################
                ###New code printer end###
                ##########################
                
                ###This is for the cases when only one line of code in the mod was changed after update, not a whole block.
                elif new_content_found == False and current_mod_line.strip() != current_submod_line.strip() and next_mod_line.strip() == next_submod_line.strip() or next_submod_line_index is None:               
                    file.write(current_mod_line + "\n")
                    
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
        
        if constant_new_content_found == False:
            os.remove(output_file)
            
    except Exception as e:
        print(f"Error writing to output file: {e}")

def main(config_file):
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
                    
                print(f"File paths: {file_paths}")
                mod_file = file_paths.get('mod_file')
                submod_file = file_paths.get('submod_file')
                
                if mod_file and submod_file:
                    output_file = os.path.splitext(submod_file)[0] + "_output" + os.path.splitext(submod_file)[1]
                    print(f"\nProcessing mod file: {mod_file}, submod file: {submod_file}, output file: {output_file}")
                    process_files(mod_file, submod_file, output_file)
                    
                else:
                    print(f"Invalid configuration line: {line}")
                    
    except Exception as e:
        print(f"Error reading config file: {e}")

####################
####THE INTERFACE###
####################
class UpToDater(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.config_file = ""
        self.setWindowTitle("Up_to_dater")
        self.setStyleSheet("background-color: black; color: white;")
        self.refresh_listbox()
    
    def initUI(self):
        ###Main layout
        main_layout = QVBoxLayout()
        
        ###Instructions label
        instruction_label = QLabel("Select or create a project file. Press 'Add Pair' to set paths to mod files. Select the original file, then your file.")
        instruction_label.setStyleSheet("color: white;")
        main_layout.addWidget(instruction_label)

        ###Files list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: black; color: white; selection-background-color: gray; selection-color: black;")
        
        scroll_area.setWidget(self.list_widget)
        main_layout.addWidget(scroll_area)

        ###Button Layout for Load Project and Create New Project File
        button_row_layout = QHBoxLayout()

        load_project_button = QPushButton("Load Project")
        load_project_button.clicked.connect(self.load_project)
        load_project_button.setStyleSheet("background-color: white; color: black;")
        button_row_layout.addWidget(load_project_button)

        new_file_button = QPushButton("Create New Project File")
        new_file_button.clicked.connect(self.create_new_file)
        new_file_button.setStyleSheet("background-color: white; color: black;")
        button_row_layout.addWidget(new_file_button)

        main_layout.addLayout(button_row_layout)

        ###Add Pair, Refresh List, Delete Pair
        button_frame = QHBoxLayout()

        add_button = QPushButton("Add Pair")
        add_button.clicked.connect(self.add_pair)
        add_button.setStyleSheet("background-color: white; color: black;")
        button_frame.addWidget(add_button)

        refresh_button = QPushButton("Refresh List")
        refresh_button.clicked.connect(self.refresh_listbox)
        refresh_button.setStyleSheet("background-color: white; color: black;")
        button_frame.addWidget(refresh_button)

        delete_button = QPushButton("Delete Pair")
        delete_button.clicked.connect(self.delete_pair)
        delete_button.setStyleSheet("background-color: white; color: black;")
        button_frame.addWidget(delete_button)

        main_layout.addLayout(button_frame)

        ###Run Script
        run_button = QPushButton("Run Script")
        run_button.clicked.connect(self.run_script)
        run_button.setStyleSheet("background-color: red; color: black;")
        main_layout.addWidget(run_button, alignment=Qt.AlignHCenter)

        ###Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white;")
        main_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        ###Setting the main layout to the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        self.resize(1200, 800)
        
    def refresh_listbox(self):
        if self.list_widget is not None:
            self.list_widget.clear()  ###Clears the list widget
        
        if not hasattr(self, 'config_file'):
            self.status_label.setText("No project file selected.")
            return
        
        try:
            with open(self.config_file, 'r') as f:
                for line in f:
                    mod_path = line.split(",")[0].split("=")[1].strip()
                    submod_path = line.split(",")[1].split("=")[1].strip()
                    mod_name = os.path.basename(mod_path)
                    submod_name = os.path.basename(submod_path)

                    ###Making submod and modlines look prettier
                    row_widget = QWidget()
                    row_layout = QHBoxLayout(row_widget)
                    mod_label = QLabel(f"mod: {mod_name}")
                    mod_label.setStyleSheet("padding-right: 20px;")
                    submod_label = QLabel(f"submod: {submod_name}")
                    
                    ###Adding labels to the layout
                    row_layout.addWidget(mod_label)
                    row_layout.addWidget(submod_label)
                    
                    ###Setting the layout and add QWidget to QListWidgetItem
                    row_widget.setLayout(row_layout)
                    list_item = QListWidgetItem(self.list_widget)
                    list_item.setSizeHint(row_widget.sizeHint())
                    self.list_widget.setItemWidget(list_item, row_widget)
                    
                    ###Connects to selection function to apply highlighting
            self.list_widget.itemSelectionChanged.connect(self.highlight_selection)

            self.status_label.setText("")
        except FileNotFoundError:
            self.status_label.setText("Error: Project file not found.")   
    
    def load_project(self):
        ###Selecting a file
        config_file, _ = QFileDialog.getOpenFileName(self, "Select Configuration File", "", "Text Files (*.txt)")
        
        ###Checking if a file was selected
        if config_file:
            self.config_file = os.path.normpath(config_file)  ###Normalizing the path, unnecessary as it turns out, but let's keep it.
            self.status_label.setText(f"Loaded project: {os.path.basename(config_file)}")
            self.refresh_listbox()
    
    def create_new_file(self):
        ###Create your thing
        new_file_name, _ = QInputDialog.getText(self, "New File Name", "Enter a name for the new project file:")
        
        if new_file_name:
            ###Defining the full path for the new file
            directory = os.path.dirname(self.config_file)  ###Add it to here
            new_file_path = os.path.join(directory, f"{new_file_name}.txt")
            
            ###You already have this file, mr. dementia
            if os.path.exists(new_file_path):
                QMessageBox.warning(self, "Error", "A file with this name already exists. Please choose a different name.")
            else:
                with open(new_file_path, 'w') as new_file:
                    new_file.write("")
                QMessageBox.information(self, "Success", f"New file created: {new_file_path}")
    
    def add_pair(self):
        mod_path, _ = QFileDialog.getOpenFileName(self, "Select Original File")
        if mod_path:
            submod_path, _ = QFileDialog.getOpenFileName(self, "Select Your File")
            if submod_path:
                with open(self.config_file, 'a') as f:
                    f.write(f"mod_file={mod_path},submod_file={submod_path}\n")
                self.refresh_listbox()

    def delete_pair(self):
    ###Getting the selected items from the list widget
        selected_items = self.list_widget.selectedItems()
        
        if selected_items:
            ###Getting the index of the selected item
            selected_index = self.list_widget.row(selected_items[0])

            ###Removing
            with open(self.config_file, 'r') as f:
                lines = f.readlines()
            with open(self.config_file, 'w') as f:
                for i, line in enumerate(lines):
                    if i != selected_index:
                        f.write(line)

            self.refresh_listbox()

            ###Determine the new selection index (one above the deleted item or the top if it was the first item)
            new_row = max(0, selected_index - 1)

            ###Setting the new row as selected if items remain in the list
            if self.list_widget.count() > 0:
                self.list_widget.setCurrentRow(new_row)

    def highlight_selection(self):
        ###Zalooping through all items to reset background color for non-selected items
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            
            if item.isSelected():
                widget.setStyleSheet("background-color: grey;")
            else:
                widget.setStyleSheet("background-color: none;")
    
    ###Delete pairs by delete key, because conviniece and stuff
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected_items = self.list_widget.selectedItems()
            if selected_items:
                self.delete_pair()

            event.accept()
        else:
            super().keyPressEvent(event)
    
    def run_script(self):
        selected_items = self.list_widget.selectedItems()
        selected_index = self.list_widget.row(selected_items[0]) if selected_items else 0
        
        try:
            with open(self.config_file, 'r') as f:
                lines = f.readlines()
            if lines:
                mod_path = lines[selected_index].split(",")[0].split("=")[1].strip()
                submod_path = lines[selected_index].split(",")[1].split("=")[1].strip()
                self.status_label.setText("Running script...")
                
                def script_thread():
                    try:
                        main(self.config_file)
                        self.status_label.setText("Script executed successfully. Or not.")
                    except Exception as e:
                        self.status_label.setText(f"Error: {str(e)}")

                thread = threading.Thread(target=script_thread)
                thread.start()
            else:
                self.status_label.setText("No paths available to run.")
        except FileNotFoundError:
            self.status_label.setText("Error: Project file not found.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    updater = UpToDater()
    updater.show()
    sys.exit(app.exec_())