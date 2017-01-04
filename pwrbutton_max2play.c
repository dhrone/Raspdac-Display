/*
 Shutdownbutton for Audiophonics Max2Play Setup
 
 build with gcc -I. -o pwrbutton pwrbutton_max2play.c -lwiringPi
 
 add this programm to autostart /etc/rc.local before "exit 0" like this:
    /opt/pwrbutton &
 
 @Copyright 2017 Stefan Rick
 @author Stefan Rick
 Mail: stefan@netzberater.de
 Web: https://www.max2play.com

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
*/

#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stdlib.h>
#include <wiringPi.h>

typedef enum { false, true } bool;

// Set WiringPi GPIO
int gpiopin = 17;
int debug = 0;
int block = 0;

void myInterrupt(void) {
  // Do not run this multiple times!
  if(block == 1)
    return;
  else
    block = 2;
  int sysreturn = 0;
  char command[100];
  sprintf(command ,"poweroff");
  sysreturn = system(command);
  printf("System: %d", sysreturn);
  return;
}

int main (int argc, char *argv[])
{
   printf("Usage: %s [-d]\n", argv[0]);
   printf(" -d Enable DEBUG output\n\n");

   int opt;
   while ((opt = getopt(argc, argv, "dc")) != -1) {
       switch (opt) {
                case 'd': debug = 1; break;
                case 'c': break; // change config Path
                default:
                    break;
                }
    }
  wiringPiSetupGpio () ;
  
  // Initialize Button Light (static ON)
  pinMode(22, OUTPUT);
  digitalWrite(22, 1);
  
  // Create Interrupt Code for Button Pressed Event
  wiringPiISR (gpiopin, INT_EDGE_RISING, &myInterrupt) ;

  printf("Initialize GPIO Pin %d\n", gpiopin);

  for (;;) {
    sleep(1000);
  }
  return 0 ;
}

