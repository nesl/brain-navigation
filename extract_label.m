

% % Specify the folder path
% folder_path = '../RWNApp_Output_Jan2024/';
% 
% % List all files in the folder
% files = dir(fullfile(folder_path, '*.mat'));
% 
% % Loop through each file
% for i = 1:numel(files)
%     % Check if the file is a regular file (not a directory)
%     if ~files(i).isdir
%         % Read the content of the file
%         file_path = fullfile(folder_path, files(i).name);
%         data = load(file_path);
%         evnts_tbl = data.evnts_tbl;
% 
%         % Define the path to save the CSV file
%         [~, file_name, ~] = fileparts(files(i).name); % Extract file name without extension
%         % Prepend "evnts_" to the filename
%         evnts_file_name = ['evnts_' file_name];
% 
%         % Define the path to save the CSV file
%         save_path = fullfile('../label_RWNApp_Output_Jan2024/', [evnts_file_name '.csv']);
% 
%         writetable(evnts_tbl, save_path);
%     end
% end


data = load('../RWNApp_Output_Jan2024/RWNApp_RW1_Walk1.mat');
% % print(data.evnts_tbl);
% evnts_tbl = data.evnts_tbl;
% 
% % Save the table as a CSV file
% writetable(evnts_tbl, '../label_RWNApp_Output_Jan2024/RWNApp_RW1_Walk1_evnts.csv');