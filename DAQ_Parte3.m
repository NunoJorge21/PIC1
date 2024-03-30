clear all
close all
clc

%% Disclaimer
%{
Since read() returns data in table columns, we will distribute ADC readings
column by column; the processing will also be done this way.
Data storage in more relevant variables (such as f_estimated, N_avg and S_ef), however, will be done in rows.
%}

%% Initialization

DAQ = daq("ni"); % DataAcquisition object
DAQ.Rate = 100*10^3; % sampling frequency
ch1 = addinput(DAQ, "Dev1", "ai0", "Voltage");
ch1.Range = [-5 5]; % set ch1 range
ch2 = addinput(DAQ, "Dev1", "ai1", "Voltage");
ch2.Range = [-1 1]; % set ch2 range

fs = DAQ.Rate;
N = 10*10^3; % number of samples for each repetition
M = 100; % number of repetitions

% Frequency axis
f = (0:N/2-1)*fs/N;

% Sensors' constants
ku = 154.951;
ki = 2.7874;
k = [ku ki];

% Memory allocation
y = zeros(N,M,2);
Y = zeros(N,M,2); % Fourier Transform of y
S = zeros(N/2,M,2); % Unilateral amplitude spectrum
S_pot = zeros(N/2,M,2); % Unilateral power spectrum in linear units
Power_VI = zeros(1,M); % istant power
f_estimated = zeros(2,M);
N_avg = zeros(2,M);
S_avg = zeros(2,M); % Average value of the signals
S_ef = zeros(2,M); % RMS value of the signals


for repetition_nr = 1:M
    data = read(DAQ, N); % Acquire data

    for page_nr = 1:2
        y(:,repetition_nr,page_nr) = k(page_nr)*table2array(data(:,page_nr));

        Y(:,repetition_nr,page_nr) = fftshift(fft(y(:,repetition_nr,page_nr))); % Fourier Transform and center in f = 0 Hz
        
        % Unilateral amplitude spectrum
        S(:,repetition_nr,page_nr) = abs(Y(length(Y(:,repetition_nr,page_nr))/2+1:end, repetition_nr,page_nr))/N;
        S(2:end-1,repetition_nr,page_nr) = 2*S(2:end-1,repetition_nr,page_nr);

        % Unilateral power spectrum in linear units
        S_pot(1,repetition_nr,page_nr) = S(1,repetition_nr,page_nr)^2; % DC component
        S_pot(2:end,repetition_nr,page_nr) = (S(2:end,repetition_nr,page_nr)./sqrt(2)).^2;

        %% Frequency estimation -> IpDFT
    
        index_max = find(S(2:end,repetition_nr,page_nr) == max(S(2:end,repetition_nr,page_nr))); % index of the maximum amplitude (must not be DC component)

        % Determine f_A and f_b
        if S(index_max+1,repetition_nr,page_nr) > S(index_max-1,repetition_nr,page_nr) || index_max == 2
            % We can never consider the DC component
            index_f_A = index_max;
            index_f_B = index_max+1;
        else % includes S(index_max+1) == S(index_max-1)
            index_f_A = index_max-1;
            index_f_B = index_max;
        end

        f_A = f(index_f_A);
        f_B = f(index_f_B);

        if S(index_max+1,repetition_nr,page_nr) ~= S(index_max-1,repetition_nr,page_nr)
            Ohmega_A = 2*pi*f_A/fs;
            Ohmega_B = 2*pi*f_B/fs;
            
            Re = real(Y(:,repetition_nr,page_nr));
            Re = Re(length(Re)/2+1:end, 1);
            Im = imag(Y(:,repetition_nr,page_nr));
            Im = Im(length(Im)/2+1:end, 1);
            
            U_A = Re(index_f_A);
            V_A = Im(index_f_A);
            U_B = Re(index_f_B);
            V_B = Im(index_f_B);
            
            K_OPT = ((V_B-V_A)*sin(Ohmega_A)+(U_B-U_A)*cos(Ohmega_A))/(U_B-U_A);
            Z_A = (V_A*(K_OPT-cos(Ohmega_A))/sin(Ohmega_A))+U_A;
            Z_B = (V_B*(K_OPT-cos(Ohmega_B))/sin(Ohmega_B))+U_B;
            f_estimated(page_nr,repetition_nr) = (fs/(2*pi))*acos((Z_B*cos(Ohmega_B)-Z_A*cos(Ohmega_A))/(Z_B-Z_A));
        else
            % If the amplitudes of the neighbour frequencies are the same, 
            % f_estimated is exactly the frequency for which the amplitude is maximum.
            % This also accounts for cases in which there is no spectral leakage. 
            f_estimated(page_nr,repetition_nr) = f_B;
        end

        N_samples_per_period = fs/f_estimated(page_nr,repetition_nr);
        N_periods(page_nr) = N/N_samples_per_period; % eventually we will need N_periods(1) and N_periods(2)
        N_complete_periods = floor(N_periods(page_nr));
        N_avg(page_nr,repetition_nr) = round(N_complete_periods*N_samples_per_period);

        %% Signal average value
        S_avg(page_nr,repetition_nr) = (1/N_avg(page_nr,repetition_nr)*sum(y(1:N_avg(page_nr,repetition_nr),repetition_nr,page_nr)));

        %% Signal RMS value
        S_ef(page_nr,repetition_nr) = sqrt((1/N_avg(page_nr,repetition_nr))*sum(y(1:N_avg(page_nr,repetition_nr),repetition_nr,page_nr).^2));
    end
    N_avg_Power_VI = floor(mean(N_avg(:,repetition_nr))); % N_avg to consider for Power_VI
    % The average value of the instant power corresponds to the active power
    Power_VI(repetition_nr) = mean(y(1:N_avg_Power_VI,repetition_nr,1).*y(1:N_avg_Power_VI,repetition_nr,2)); % active power
end

% Mean(x,2) performs the mean of x, row by row
f_estimated_mean = round(mean(f_estimated,2)); % these voltage and current signals should have the same frequency
Power_VI_mean = mean(Power_VI); % average active power
S_ef_mean = mean(S_ef,2);
N_avg_mean = mean(N_avg,2);
N_avg_mean = mean(N_avg_mean);

% Unilateral average power spectrum in linear units
S_pot_mean = mean(S_pot,2);

% Unilateral average power spectrum in dB
S_pot_dB = 10*log10(S_pot_mean); 


%% THD

for n = 1:2
    harmonic = 3;
    [~, aux] = min(abs(f - harmonic*f_estimated_mean(n))); % find the index of the value of f that is the closest to f_estimated_mean(n)
    sum_power = 0.0;

    while aux < length(f)
        sum_power = sum_power + S_pot_mean(aux,1,n); % S_pot_mean is the mean of the squares of the RMS values of the components aux
        
        % The signals we are working with only have odd harmonics
        harmonic = harmonic + 2;
        [~, aux] = min(abs(f - harmonic*f_estimated_mean(n)));
    end

    THD(n) = 20*log10(sqrt(sum_power/S_pot(index(n),1,n)));
end


%% RMS value of the first 11 harmonics (including fundamental)
Uk_EF = zeros(1,11);
Uk_EF_dB = zeros(1,11);
Ik_EF = zeros(1,11);
Ik_EF_dB = zeros(1,11);

[~, index(1)] = min(abs(f - f_estimated_mean(1)));
[~, index(2)] = min(abs(f - f_estimated_mean(2)));

n = 1;
while n <= 11 && index(1) <= length(S) && index(2) <= length(S)
    % The value that is divided by sqrt(2) is the average value, accross all the
    % repetitions, of the amplitude in line index (1 or 2)
    Uk_EF(n) = (sum(S(index(1),:,1))/size(S,2))/sqrt(2);
    Ik_EF(n) = (sum(S(index(2),:,2))/size(S,2))/sqrt(2);

    n = n + 1;
    [~, index(1)] = min(abs(f - n*f_estimated_mean(1)));
    [~, index(2)] = min(abs(f - n*f_estimated_mean(2)));
end

Uk_EF_dB = 20*log10(Uk_EF);
Ik_EF_dB = 20*log10(Ik_EF);


%% Apparent Power

P_apparent = S_ef_mean(1)*S_ef_mean(2);


%% Active Power

P_active = Power_VI_mean;

% The uncertainty to consider is the standard deviation of the experimental value
uP_active_absolute = sqrt((1/(M*(M-1)))*sum((Power_VI(1:M)-Power_VI_mean).^2));
uP_active_relative = 100*uP_active_absolute/P_active;


%% Plot

for n = 1:2
    tf(n) = N/fs; % corresponds to sampling duration

    if N_periods(n) > 5
        tf(n) = 5*tf(n)/N_periods(n);
        % this tf is the instant when 5 periods of the signal are completed
    end
end

t = linspace(0, N/fs, N);

subplot(2,2,1), hold on
plot(t,y(:,end,1)) % y(:,end,1) is the signal that has the current value of N_periods(1) periods
title("Network Voltage")
xlabel("Time [s]")
ylabel("Amplitude [V]")
xlim([0 tf(1)]) % limit time axes in order to present 5 periods or less

subplot(2,2,2), hold on
plot(t,y(:,end,2))
title("Load Current")
xlabel("Time [s]")
ylabel("Amplitude [A]")
xlim([0 tf(2)])

subplot(2,2,3), hold on
plot(f,S_pot_dB(:,1,1))
title("Unilateral Average Power Spectrum of the Network Voltage")
xlabel("Frequency [Hz]")
ylabel("Amplitude [dBV]")
%xlim([0 1400])
xlim([0 floor(fs/2)]) % limit frequency axes to half of the sampling frequency

subplot(2,2,4)
plot(f,S_pot_dB(:,1,2))
title("Unilateral Average Power Spectrum of the Load Current")
xlabel("Frequency [Hz]")
ylabel("Amplitude [dBA]")
%xlim([0 1400])
xlim([0 floor(fs/2)])
hold off