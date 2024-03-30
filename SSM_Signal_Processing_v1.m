clear all
close all
clc

situation = 1;

data = readtable("rp2040_data5.csv"); % Read data collected by Arduino's mic
data = table2array(data);

t = data(:,1); % time array
y = data(:,2); % signal array

fs = 1/(t(2)-t(1)); % sampling frequency
N = length(t); % number of samples
sampling_duration = t(end); % sampling duration

Y = fftshift(fft(y)); % Fourier Transform and center in f = 0 Hz
f = (0:ceil(length(Y)/2)-1)*fs/length(Y); % frequency axis

% Unilateral amplitude spectrum
S = abs(Y(floor(length(Y)/2)+1:end, 1))/N;
S(2:end-1,1) = 2*S(2:end-1,1);

S_pot = (S./sqrt(2)).^2;
% Unilateral power spectrum
S_pot_dB = 10*log10(S_pot);

%% Frequency estimation -> IpDFT

index_max = find(S == max(S(2:end,1))); % index of the maximum amplitude (must not be DC component)

% Determine f_A and f_b
if S(index_max+1) > S(index_max-1) || index_max == 2
    % We can never consider the DC component
    index_f_A = index_max;
    index_f_B = index_max+1;
else % includes S(index_max+1) == S(index_max-1)
    index_f_A = index_max-1;
    index_f_B = index_max;
end

f_A = f(index_f_A);
f_B = f(index_f_B);

if S(index_max+1) ~= S(index_max-1)
    Ohmega_A = 2*pi*f_A/fs;
    Ohmega_B = 2*pi*f_B/fs;
    
    Re = real(Y);
    Re = Re(floor(length(Re)/2)+1:end, 1);
    Im = imag(Y);
    Im = Im(floor(length(Im)/2)+1:end, 1);
    
    U_A = Re(index_f_A);
    V_A = Im(index_f_A);
    U_B = Re(index_f_B);
    V_B = Im(index_f_B);
    
    K_OPT = ((V_B-V_A)*sin(Ohmega_A)+(U_B-U_A)*cos(Ohmega_A))/(U_B-U_A);
    Z_A = (V_A*(K_OPT-cos(Ohmega_A))/sin(Ohmega_A))+U_A;
    Z_B = (V_B*(K_OPT-cos(Ohmega_B))/sin(Ohmega_B))+U_B;
    f_estimated = (fs/(2*pi))*acos((Z_B*cos(Ohmega_B)-Z_A*cos(Ohmega_A))/(Z_B-Z_A));
else
    % If the amplitudes of the neighbour frequencies are the same, 
    % f_estimated is exactly the frequency for which the amplitude is maximum.
    % This also accounts for cases in which there is no spectral leakage. 
    f_estimated = f_B;
end

N_samples_per_period = fs/f_estimated;
N_periods = N/N_samples_per_period;
N_complete_periods = floor(N_periods);
N_avg = round(N_complete_periods*N_samples_per_period);

%% Signal average value

S_avg = (1/N_avg)*sum(y, [1, N_avg]);

%% Signal RMS value

S_ef = sqrt((1/N_avg)*sum(y.^2, [1, N_avg]));


%% Total Harmonic Distortion

harmonic = 3;
[~, aux] = min(abs(f - harmonic*f_estimated));
sum_power = 0.0;

while aux < length(f)
    % Sum the power of each harmonic
    sum_power = sum_power + S_pot(aux); % S_pot = square of the RMS value of the component aux

    % The signals we are working with only have odd harmonics
    harmonic = harmonic + 2;
    [~, aux] = min(abs(f - harmonic*f_estimated));
end

THD = 20*log10(sqrt(sum_power/S_pot(index_max)));

    
%% Plot

title_str = sprintf("f_{estimated} = %.2f Hz, S_{avg} = %.2f V, S_{ef} = %.2f V," + ...
    " N = %d samples, f_s = %d Hz", f_estimated, S_avg, S_ef, N, ...
    fs);

%{
tf = sampling_duration;

if N_periods > 5
    tf = 5*tf/N_periods;
    % this tf is the instant when 5 periods of the signal are completed
end
%}

subplot(2,1,1), hold on
plot(t,y)
title(title_str)
xlabel("Time [s]")
ylabel("Amplitude [V]")
% xlim([0 tf]) % limit time axes in order to present 5 periods or less
subplot(2,1,2)
plot(f,S_pot_dB)
title("Unilateral Power Spectrum")
xlabel("Frequency [Hz]")
ylabel("Amplitude [dB]")
xlim([0 floor(fs/2)]) % limit frequency axes to half of the sampling frequency
hold off