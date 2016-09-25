#!/bin/bash

echo "Audiophonics Shutdown script starting..."
echo "Asserting pins : "
echo "ShutDown : GPIO17=in, Low"
echo "BootOK   : GPIO22=out, High"

/usr/bin/gpio -g mode 17 in
/usr/bin/gpio -g write 17 0
/usr/bin/gpio -g mode 22 out
/usr/bin/gpio -g write 22 1

while [ 1 ]; do
  if [ "$(/usr/bin/gpio -g read 17)" = "1" ]; then
        echo "ShutDown order received, RaspBerry pi will now enter in standby mode..."
        systemctl poweroff
        break
  fi
  /bin/sleep 0.25
done

exit 0
