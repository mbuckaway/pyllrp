
#------------------------------------------------------
# Copyright (C) 2013-2019 Edward Sitarski
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
# and associated documentation files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
# BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
import re
import socket
import subprocess
from .pyllrp import UnpackMessageFromSocket, ConnectionAttemptEvent_Parameter, ConnectionAttemptStatusType

def GetDefaultHost():
    DEFAULT_HOST = socket.gethostbyname(socket.gethostname())
    if DEFAULT_HOST in ('127.0.0.1', '127.0.1.1'):
        reSplit = re.compile('[: \t]+')
        try:
            co = subprocess.Popen(['ifconfig'], stdout=subprocess.PIPE)
            ifconfig = co.stdout.read().decode()
            for line in ifconfig.split('\n'):
                line = line.strip()
                try:
                    if line.startswith('inet addr:'):
                        fields = reSplit.split( line )
                        addr = fields[2]
                        if addr != '127.0.0.1':
                            DEFAULT_HOST = addr
                            break
                except Exception as e:
                    pass
        except Exception as e:
            pass
    return DEFAULT_HOST
    
def findImpinjHost( impinjPort=5084 ):
    ''' Search ip addresses adjacent to the computer in an attempt to find the reader. '''
    ip = [int(i) for i in GetDefaultHost().split('.')]
    j = 0
    for i in range(14):
        j = -j if j > 0 else -j + 1
        
        ipTest = list( ip )
        ipTest[-1] += j
        if not (0 <= ipTest[-1] < 256):
            continue
            
        impinjHost = '.'.join( '{}'.format(v) for v in ipTest )
        
        readerSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        readerSocket.settimeout( 4.0 )
        try:
            readerSocket.connect( (impinjHost, impinjPort) )
        except Exception as e:
            continue
        
        try:
            response = UnpackMessageFromSocket( readerSocket )
        except Exception as e:
            readerSocket.close()
            continue
            
        readerSocket.close()
        
        # Check if the connection succeeded.
        connectionAttemptEvent = response.getFirstParameterByClass(ConnectionAttemptEvent_Parameter)
        if connectionAttemptEvent and connectionAttemptEvent.Status == ConnectionAttemptStatusType.Success:
            return impinjHost
            
    return None

def AutoDetect( impinjPort=5084 ):
    return findImpinjHost(impinjPort), GetDefaultHost()
        
if __name__ == '__main__':
    print( AutoDetect() )

