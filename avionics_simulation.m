%% ============================================================
%% Avionics Sensor Data Analysis & Anomaly Detection
%% Script   : avionics_simulation.m
%% Purpose  : Load NASA DASHlink .mat files from 3 aircraft tail
%%            folders, extract 6 key flight parameters, combine
%%            all flights into one dataset, and export CSV files
%%            for Python analysis and cross-validation.
%% Author   : P B Aruljith
%% ============================================================

clc; clear;

%% ── CONFIGURATION ────────────────────────────────────────────
%  Update these folder paths to match your local directory
folders = {
    'D:/AnalyticsProjects/Flight Data/Tail_685_1/';
    'D:/AnalyticsProjects/Flight Data/Tail_652_1/';
    'D:/AnalyticsProjects/Flight Data/Tail_678_1/'
};

output_csv  = 'D:/AnalyticsProjects/Flight Data/avionics_export.csv';
output_corr = 'D:/AnalyticsProjects/Flight Data/matlab_corr.csv';

%% ── INITIALISE ARRAYS ────────────────────────────────────────
all_alt = []; all_airspd = []; all_pitch = [];
all_roll = []; all_eng   = []; all_temp  = [];
all_flightid = [];
flight_counter = 0;

%% ── LOAD ALL FILES ACROSS ALL FOLDERS ───────────────────────
for f = 1:length(folders)
    files = dir(fullfile(folders{f}, '*.mat'));
    fprintf('\nFolder %d — %s\n', f, folders{f});
    fprintf('Files found: %d\n', length(files));

    for i = 1:length(files)
        filepath = fullfile(folders{f}, files(i).name);
        try
            d = load(filepath);

            %% Altitude — try multiple field name variants
            if isfield(d, 'ALT'),       alt = d.ALT.data(:);
            elseif isfield(d, 'BALT'),  alt = d.BALT.data(:);
            else,                        alt = nan(100,1); end

            %% Airspeed — Calibrated or Indicated
            if isfield(d, 'CAS'),       airspd = d.CAS.data(:);
            elseif isfield(d, 'IAS'),   airspd = d.IAS.data(:);
            else,                        airspd = nan(100,1); end

            %% Pitch angle
            if isfield(d, 'PTCH'),      pitch = d.PTCH.data(:);
            elseif isfield(d, 'PITCH'), pitch = d.PITCH.data(:);
            else,                        pitch = nan(100,1); end

            %% Roll angle
            if isfield(d, 'ROLL'),      roll = d.ROLL.data(:);
            else,                        roll = nan(100,1); end

            %% Engine N1 speed — try left/right engine variants
            if isfield(d, 'N1'),        eng = d.N1.data(:);
            elseif isfield(d, 'N1L'),   eng = d.N1L.data(:);
            elseif isfield(d, 'N1R'),   eng = d.N1R.data(:);
            elseif isfield(d, 'ENG'),   eng = d.ENG.data(:);
            else,                        eng = nan(100,1); end

            %% Temperature — Total/Static/Outside Air
            if isfield(d, 'TAT'),       temp = d.TAT.data(:);
            elseif isfield(d, 'SAT'),   temp = d.SAT.data(:);
            elseif isfield(d, 'OAT'),   temp = d.OAT.data(:);
            else,                        temp = nan(100,1); end

            %% Trim all channels to equal length within this file
            n = min([length(alt), length(airspd), length(pitch), ...
                     length(roll), length(eng), length(temp)]);

            flight_counter = flight_counter + 1;

            %% Append this flight's data to master arrays
            all_alt      = [all_alt;      alt(1:n)];
            all_airspd   = [all_airspd;   airspd(1:n)];
            all_pitch    = [all_pitch;    pitch(1:n)];
            all_roll     = [all_roll;     roll(1:n)];
            all_eng      = [all_eng;      eng(1:n)];
            all_temp     = [all_temp;     temp(1:n)];
            all_flightid = [all_flightid; ones(n,1) * flight_counter];

            fprintf('  Loaded: %s  (%d records)\n', files(i).name, n);

        catch e
            fprintf('  Skipped: %s — %s\n', files(i).name, e.message);
        end
    end
end

%% ── FINAL TRIM ───────────────────────────────────────────────
n = min([length(all_alt), length(all_airspd), length(all_pitch), ...
         length(all_roll), length(all_eng),   length(all_temp)]);

fprintf('\n=============================\n');
fprintf('Total flights loaded : %d\n', flight_counter);
fprintf('Total records        : %d\n', n);
fprintf('=============================\n');

%% ── EXPORT MAIN CSV ──────────────────────────────────────────
fid = fopen(output_csv, 'w');
if fid == -1
    fprintf('ERROR: Cannot write to %s\nSaving to current directory.\n', output_csv);
    fid = fopen('avionics_export.csv', 'w');
end

fprintf(fid, 'FlightID,Altitude,Airspeed,Pitch,Roll,EngineN1,Temperature\n');
for i = 1:n
    fprintf(fid, '%d,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f\n', ...
        all_flightid(i), all_alt(i), all_airspd(i), all_pitch(i), ...
        all_roll(i), all_eng(i), all_temp(i));
end
fclose(fid);
fprintf('Exported main CSV  : %s\n', output_csv);

%% ── COMPUTE CORRELATION MATRIX ───────────────────────────────
data_matrix = [all_alt(1:n), all_airspd(1:n), all_pitch(1:n), ...
               all_roll(1:n), all_eng(1:n),   all_temp(1:n)];

%% Replace NaN with column mean before correlation (Octave-compatible)
for col = 1:size(data_matrix, 2)
    col_mean = mean(data_matrix(~isnan(data_matrix(:,col)), col));
    data_matrix(isnan(data_matrix(:,col)), col) = col_mean;
end

corr_matrix = corr(data_matrix);

%% ── EXPORT CORRELATION CSV ───────────────────────────────────
fid = fopen(output_corr, 'w');
if fid == -1
    fid = fopen('matlab_corr.csv', 'w');
end
for i = 1:size(corr_matrix, 1)
    fprintf(fid, '%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n', corr_matrix(i,:));
end
fclose(fid);
fprintf('Exported corr CSV  : %s\n', output_corr);
fprintf('\nDone. Ready for Python pipeline.\n');
