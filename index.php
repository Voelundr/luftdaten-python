<?php
ini_set("display_errors", "0");
// error_reporting(E_ALL);
$host = "127.0.0.1";
$port = 8367;
if(!($socket = socket_create(AF_INET, SOCK_STREAM, 0))) {
    die("Could not create socket.<br>\n");
}
// echo "Socket created<br>\n";
if(!($result = socket_connect($socket, $host, $port))) {
    die("Sensoren sind offline.<br>\n");
}
// echo "Connection established.<br>\n";
if(!($result = socket_read($socket, 1024))) {
    die("Could not read server response.<br>\n");
}
// echo "Reply From Server: ".unserialize($result);
$data_array = unserialize($result);
// print_r($data_array);
socket_close($socket);
?>
<!DOCTYPE html>
<html>
 <head>
  <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
  <title>
   Wetter und Feinstaubstation
  </title>
 </head>
 <body>
  <h3>
   BME280 Sensor
  </h3>
  <div id="temp">
   Temperatur: <?php echo sprintf("%.2f", $data_array[2]); ?> °C
  </div>
  <div id="hum">
   rel. Luftfeuchtigkeit: <?php echo sprintf("%.2f", $data_array[3]); ?> %
  </div>
  <div id="press">
   Luftdruck: <?php echo sprintf("%.2f", $data_array[4]/100); ?> hPa
  </div>
  <div id="eqtemp">
   <?php $pressinhpa = $data_array[4]/100; ?>
   berechnete Äquivalenttemperatur: <?php echo sprintf("%.2f", ($data_array[2]+94.341*(($data_array[3]*pow(10, ((7.45*$data_array[2])/(235+$data_array[2]))))/$pressinhpa))); ?> °C
   <br><i>Bei einer Äquivalenttemperatur über 50-55 °C wird die Luft als schwül empfunden.</i> <!-- calculate and disaplay Equivalent temperature -->
  </div>
<!--
  <h3>
   DHT22 Sensor
  </h3>
  <div id="temp2">
   Temperatur: <?php /* echo sprintf("%.2f", $data_array[6]); */ ?> °C
  </div>
  <div id="hum2">
   Luftfeuchtigkeit: <?php /* echo sprintf("%.2f", $data_array[5]); */ ?> %
  </div>
-->
  <h3>
   Nova Fitness SDS011 Feinstaubsensor
  </h3>
  <div id="pm10">
   PM 10: <?php echo sprintf("%f", $data_array[0]); ?> µg/m³
  </div>
  <div id="pm25">
   PM 2.5: <?php echo sprintf("%f", $data_array[1]); ?> µg/m³
  </div>
  <h3 id="date">
   Stand: <?php echo $data_array[5]; ?>
  </h3>
  <h3>
   <a href="http://www.madavi.de/sensor/graph.php?sensor={your sensorID}-sds011"> <!-- insert sensorID -->
    Link zum Verlauf der Feinstaubwerte
   </a>
  </h3>
  <h3>
   <a href="http://www.madavi.de/sensor/graph.php?sensor={your sensorID}-bme280"> <!-- insert sensorID -->
    Link zum Verlauf der Wetterdaten
   </a>
  </h3>
  <h3>
   <a href="https://opensensemap.org/explore/{your openSenseBox ID}"> <!-- insert ID -->
    Sensor auf openSenseMap
   </a>
  </h3>
 </body>
</html>
