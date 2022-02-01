import pyautogui, os, cv2
import numpy as np
from flask import Flask, render_template, request, Response
app = Flask(__name__)
import logging
from time import sleep
log = logging.getLogger('werkzeug')
#log.disabled = True  #log.setLevel(logging.ERROR)


xpy=0
ypy=0

@app.route('/')
def index():
    return render_template("a.html", xpy=xpy, ypy=ypy)

submit_counter, pos_counter = 0,0
xpos, ypos = 0,0
@app.route('/flasktest' , methods=["POST"])
def handler():
   global xpos, ypos, submit_counter, pos_counter
   themostresentvalue  = str(request.form)
   submit_counter += 1
   #print("submit_counter", submit_counter)
   #print(themostresentvalue)
   a, b = themostresentvalue.split(":")
   a = a.replace("[","").replace('"',"").replace("ImmutableMultiDict(('","")
   b = b.replace("]","").replace('"',"").replace("', ''))","")
   xpos,ypos = int(float(a)*float(pyautogui.size()[0])), int(float(b) *float(pyautogui.size()[1]))
   pyautogui.moveTo(xpos,ypos)
   #print("pos_counter", pos_counter)
   #print("postioninng happend at "+ a + " and " + b)
   pos_counter += 1
   xpy,ypy = pyautogui.position().x/pyautogui.size()[0] , pyautogui.position().y/pyautogui.size()[1]
   #print(xpy, ypy)
   return render_template("a.html",xpy=xpy, ypy=ypy )


def mark_mouse_postion(x,y,img):
    #print(x , y)
    for i in range(x-5,x+5):
        for j in range(y-5,y+5):
            try:
              img[j][i]  =  np.array([0,0,255])
            except:
                continue
    return img


def gen_frames(): 
    global xpos, ypos 
    while True:
        img = pyautogui.screenshot()
        frame = np.array(img)
        n = 1
        #frame = cv2.resize(frame, (int(1920 * n), int(1080* n)))
        frame = mark_mouse_postion(xpos,ypos,frame)
        
        ret, buffer = cv2.imencode('.jpg', frame) #  
        frame = buffer.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames() , mimetype='multipart/x-mixed-replace; boundary=frame')



template= """
<html>
<head>
<title> Track Mouse </title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script type="text/javascript">

let pageCoords = [];

xpy = {{xyp}} 
ypy = {{ypy}}
console.log(xpy)
console.log(ypy)
window.onmousemove = (e) => {
    // 
    XX =  e.pageX / window.innerWidth;
    YY = e.pageY  / window.innerHeight;
    x = XX.toString()
    y = YY.toString()
    str = x + ":" +  y
    const XHR = new XMLHttpRequest();
    XHR.open('POST', '/flasktest',true)
    XHR.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
    XHR.send(JSON.stringify(str))  
    str = ""
    document.Form1.xjs.value = x
    document.Form1.yjs.value = y
    //document.Form1.xpy.value = xpy
    //document.Form1.ypy.value = ypy
}

            function resize()
            {
                body.style.height = window.innerHeight  + "px";
                body.style.height = window.innerWidth + "px";
            }
            resize();
            window.onresize = function() {
                resize();
            };

</script>

<style>
body, html {
  height: 100%;
  width: 100%;
}

.bg {
  margin: 0px;
  padding: 0px;
  background-image: url("{{ url_for('video_feed') }}");
  height: 100%;
  width:100%;
  background-position: center center;
  background-repeat: no-repeat;
  background-size: cover;

}
</style>
</head>
<body class="bg" id="bg">
#POSX: <input type="text" name="xjs"><br>
#POSy: <input type="text" name="yjs"><br>
</body>
</html>
"""


def create_template():
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    if not os.path.exists(templates_dir):
      os.mkdir(templates_dir)
    
    html_template = os.path.join(templates_dir, "a.html")
    with open(html_template, "w") as f:
      f.write(template)
    

if __name__ == '__main__':
   create_template()
   app.run(host='192.168.1.179',port=80)


#<form name="Form1">
#POSX: <input type="text" name="xjs"><br>
#POSy: <input type="text" name="yjs"><br>
#POSxpython: <input type="text" name="xpy" value="{{xpy}}"><br>
#POSypython: <input type="text" name="ypy" value="{{ypy}}"><br>
#</form>

### <form name="Form1" style="visibility: hidden;">
### POSX: <input type="text" name="x"><br>
### POSY: <input type="text" name="y"><br>
### WinX: <input type="text" name="wx"><br>
### WinY: <input type="text" name="wy"><br>
### </form>

##    document.Form1.wx.value = window.innerWidth;
##    document.Form1.wy.value = window.innerHeight;
##  window.addEventListener('load', () => {
##      document.Form1.wx.value = window.innerWidth;
##      document.Form1.wy.value = window.innerHeight;
##     })
##  
##  window.addEventListener('resize', () => {
##      var a = window.innerWidth;
##      var b = window.innerHeight;
##  
##     })
#### <img id="scrr" src="{{ url_for('video_feed') }}" width="100%">