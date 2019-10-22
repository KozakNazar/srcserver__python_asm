#######################################################################
# N.Kozak // Lviv'2019 // example server Python(LLNW)-Asm for pkt3 SP #
#                         file: server.py                             #
#                                                              files: #
#                                                              calc.s #
#                                                           server.py #
#                                                                     #
#                                                   *extended version #
#######################################################################
import sys
import ctypes
import socket
import re

# to implement a constant in Python
class CONSTANT(object): 
    def __init__(self, CONSTANT): self._CONSTANT = CONSTANT
    @property 
    def CONSTANT(self): return self._CONSTANT

HOST = '' # all available interfaces
PORT = 80 # non-privileged port

def buildResponse(usePostSubmit, calc, b2, c1, d2, e1, f2):
    K = CONSTANT(0x00025630) #K.CONSTANT - constant value
	
    http_response_fmt = """HTTP/1.1 200 OK
Date: Mon, 27 Jul 2009 12:28:53 GMT
Server: Apache/2.2.14 (Win32)
Last-Modified: Wed, 22 Jul 2009 19:15:56 GMT
Content-Length: {:d}
Status: 200
Content-Type: text/html
Connection: Closed

{:s}""";

    html_code_fmt__withGetSubmit = """<html>
<head>
<link rel="icon" href="data:;base64,=">
</head>
<body>

<form action="/setSettings" method="get">
<h1>Settings:</h1>
<p>Select mode:</p>  
  <input type="radio" name="mode" value="1"> mode 1<br>
  <input type="radio" name="mode" value="2"> mode 2<br>
  <input type="radio" name="mode" value="3"> mode 3<br> 
<p>Change used http-method:</p>
  <input type="radio" name="http_method" value="0" checked="checked"> GET<br>
  <input type="radio" name="http_method" value="1"> POST<br> 

  <input type="submit" value="Submit parameters and reload page" text="">
</form>
<h1>Compute board:</h1>
<button type="submit" form="calcData">Send values by GET and compute result</button>

<form id="calcData"  method="get" action="callCalc">

<h2>X = K + B2 - D2/C1 + E1*F2</h2>
<h2>--------------------------</h2>
<h2>K = {:d}</h2>
<h2>B = <input name="B" type="text" value="{:f}"></h2>
<h2>C = <input name="C" type="text" value="{:f}"></h2>
<h2>D = <input name="D" type="text" value="{:f}"></h2>
<h2>E = <input name="E" type="text" value="{:f}"></h2>
<h2>F = <input name="F" type="text" value="{:f}"></h2>
<h2>-------</h2>
<h2>X(Assembly) = {:f}</h2>
<h2>X(Python) = {:f}</h2>
<h2>--------------------------</h2>
<input type="submit" value="Send values by GET and compute result">

</form>
</body>
</html>""";	

    html_code_fmt__withPostSubmit = """<html>
<head>
<link rel="icon" href="data:;base64,=">
</head>
<body>

<form action="/setSettings" method="post">
<h1>Settings:</h1>
<p>Select mode:</p>  
  <input type="radio" name="mode" value="1"> mode 1<br>
  <input type="radio" name="mode" value="2"> mode 2<br>
  <input type="radio" name="mode" value="3"> mode 3<br> 
<p>Change used http-method:</p>
  <input type="radio" name="http_method" value="0"> GET<br>
  <input type="radio" name="http_method" value="1" checked="checked"> POST<br> 

  <input type="submit" value="Submit parameters and reload page" text="">
</form>
<h1>Compute board:</h1>
<button type="submit" form="calcData">Send values by POST and compute result</button>

<form id="calcData"  method="post" action="callCalc">

<h2>X = K + B2 - D2/C1 + E1*F2</h2>
<h2>--------------------------</h2>
<h2>K = {:d}</h2>
<h2>B = <input name="B" type="text" value="{:f}"></h2>
<h2>C = <input name="C" type="text" value="{:f}"></h2>
<h2>D = <input name="D" type="text" value="{:f}"></h2>
<h2>E = <input name="E" type="text" value="{:f}"></h2>
<h2>F = <input name="F" type="text" value="{:f}"></h2>
<h2>-------</h2>
<h2>X(Assembly) = {:f}</h2>
<h2>X(Python) = {:f}</h2>
<h2>--------------------------</h2>
<input type="submit" value="Send values by POST and compute result">

</form>
</body>
</html>""";
			
    html_code_fmt = html_code_fmt__withGetSubmit;
	
    if usePostSubmit:
        html_code_fmt = html_code_fmt__withPostSubmit;
		
    html_code = html_code_fmt .format (K.CONSTANT, b2, c1, d2, e1, f2, calc(b2, c1, d2, e1, f2), K.CONSTANT + b2 - d2/c1 + e1*f2)
	
    return http_response_fmt .format (len(html_code), html_code)

def handleClient(conn, usePostSubmit, calc, b2, c1, d2, e1, f2) :
    data = conn.recv(2048)	
    message: str = data.decode('ascii')
    #message: str = data.decode('ascii', 'surrogateescape')	
    #message: str = data.decode('utf-8')	
	
    http_method_key = "http_method="; 
    B_key = "B=";
    C_key = "C=";
    D_key = "D=";
    E_key = "E=";
    F_key = "F="; 
	
    indexPOSTsubstring = message.find("POST")
    indexPOSTValues = message.find("\r\n\r\n")
    if (indexPOSTsubstring > -1) and (indexPOSTValues > -1):	
        usePostSubmit = True

        index = message[indexPOSTValues:].find(http_method_key)
        if index > -1 :		
            index += indexPOSTValues;		
            usePostSubmitValue: int = 0;
            if usePostSubmit:
                usePostSubmitValue = 1;
            returnMatchObject = re.match(r'[-+]?(0[xX][\dA-Fa-f]+|0[0-7]*|\d+)', message[index + len(http_method_key):])
            if(returnMatchObject):			
                usePostSubmitValue = float(returnMatchObject.group(0))						
            usePostSubmit = True;
            if usePostSubmitValue == 0:              
                usePostSubmit = False;

        index = message[indexPOSTValues:].find(B_key)
        if index > -1 :
            index += indexPOSTValues;	            
            returnMatchObject = re.match(r'[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?', message[index + len(B_key):])
            if(returnMatchObject):			
                b2 = float(returnMatchObject.group(0))	            
        index = message[indexPOSTValues:].find(C_key)
        if index > -1 :
            index += indexPOSTValues;	            
            returnMatchObject = re.match(r'[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?', message[index + len(C_key):])
            if(returnMatchObject):			
                c1 = float(returnMatchObject.group(0))		
        index = message[indexPOSTValues:].find(D_key)
        if index > -1 :
            index += indexPOSTValues;	            
            returnMatchObject = re.match(r'[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?', message[index + len(D_key):])
            if(returnMatchObject):			
                d2 = float(returnMatchObject.group(0))		
        index = message[indexPOSTValues:].find(E_key)
        if index > -1 :
            index += indexPOSTValues;	            
            returnMatchObject = re.match(r'[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?', message[index + len(E_key):])
            if(returnMatchObject):			
                e1 = float(returnMatchObject.group(0))		
        index = message[indexPOSTValues:].find(F_key)
        if index > -1 :
            index += indexPOSTValues;	            
            returnMatchObject = re.match(r'[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?', message[index + len(F_key):])
            if(returnMatchObject):			
                f2 = float(returnMatchObject.group(0))		
    else:
	
        index = message.find(http_method_key)
        if index > -1 :
            usePostSubmitValue: int = 0;
            if usePostSubmit :
                usePostSubmitValue = 1;
            returnMatchObject = re.match(r'[-+]?(0[xX][\dA-Fa-f]+|0[0-7]*|\d+)', message[index + len(http_method_key):])
            if(returnMatchObject):			
                usePostSubmitValue = float(returnMatchObject.group(0))				
            usePostSubmit = True;	
            if usePostSubmitValue == 0 :				
                usePostSubmit = False;     
        else:
            index = message.find(B_key)
            if index > -1 :
                usePostSubmit = False
                returnMatchObject = re.match(r'[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?', message[index + len(B_key):])
                if(returnMatchObject):			
                    b2 = float(returnMatchObject.group(0))												   
            index = message.find(C_key)
            if index > -1 :
                usePostSubmit = False
                returnMatchObject = re.match(r'[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?', message[index + len(C_key):])
                if(returnMatchObject):			
                    c1 = float(returnMatchObject.group(0))			
            index = message.find(D_key)
            if index > -1 :
                usePostSubmit = False
                returnMatchObject = re.match(r'[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?', message[index + len(D_key):])
                if(returnMatchObject):			
                    d2 = float(returnMatchObject.group(0))			
            index = message.find(E_key)
            if index > -1 :
                usePostSubmit = False
                returnMatchObject = re.match(r'[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?', message[index + len(E_key):])
                if(returnMatchObject):			
                    e1 = float(returnMatchObject.group(0))			
            index = message.find(F_key)
            if index > -1 :
                usePostSubmit = False
                returnMatchObject = re.match(r'[-+]?(\d+([.,]\d*)?|[.,]\d+)([eE][-+]?\d+)?', message[index + len(F_key):])
                if(returnMatchObject):			
                    f2 = float(returnMatchObject.group(0))			
	
    conn.sendall(buildResponse(usePostSubmit, calc, b2, c1, d2, e1, f2).encode())
    conn.close()
	
    return usePostSubmit, b2, c1, d2, e1, f2
	
fun = ctypes.CDLL("calc.so")
fun.calc.argtypes = [ctypes.c_double, ctypes.c_float, ctypes.c_double, ctypes.c_float, ctypes.c_double]
fun.calc.restype = ctypes.c_float
calc = fun.calc;	
	
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    usePostSubmit: bool = True;                # defaault value
    
    b2: float = 10               ## float64 ## # defaault value
    c1: float = 20               ## float32 ## # defaault value 
    d2: float = 30               ## float64 ## # defaault value 
    e1: float = 40               ## float32 ## # defaault value 
    f2: float = 50               ## float64 ## # defaault value 
	
    s.bind((HOST, PORT))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            usePostSubmit, b2, c1, d2, e1, f2 = handleClient(conn, usePostSubmit, calc, b2, c1, d2, e1, f2)