#!/bin/bash
echo "OK" > /tmp/devsync-handler.txt
/usr/bin/sshpass -p 'secret' ssh user@address 'echo OK > /tmp/devsync-handler.txt; sync'
