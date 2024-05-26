# LoRa

Nesta pasta estão os protótipos para o transmissor, o recetor e o código de python para visualizar os dados recebidos. 
O código "Sender.ino" envia as amostras de aúdio RAW e demora 20,2 segudos a completar a tarefa. Por outro lado, o código "SenderFFT.ino" envia metade das amostras, uma vez que os dados emitidos são da transformada de fourier unilateral (NÃO É O ESPETRO DE POTÊNCIA) e, assim sendo, demora cerca de 10 segundos. 
O código ReadPythonReceiver.py é compatível exclusivamente com "SenderFFT.ino" e "Receiver.ino". Não esquecer de alterar a linha do "Serial" para utilizadores de LINUX.
Também publiquei as conexões dos pinos. Na imagem a cor que representa cada um dos fios é a cor dos fios realmente utilizados e basta conectar as cores.
Não incluí GPS funcional.
Abraço
