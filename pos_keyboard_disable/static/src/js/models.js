
 document.onkeydown = function (e)
 {
 console.log("D<D<<Donkeydown",e.target.localName,e.target.localName!='input' && e.key=='2')
 if (e.target.localName!='input'){
 $('.remove-line-button').click()

 }



 }


  document.onkeypress = function (e)
 {
 console.log("D<D<<Donkeydown",e.target.localName,e.target.localName!='input' && e.key=='2')
 if (e.target.localName!='input'){
 $('.remove-line-button').click()
;
             }



 }

   document.onkeyup = function (e)
 {
 console.log("D<D<<Donkeydown",e.target.localName,e.target.localName!='input' && e.key=='2')
 if (e.target.localName!='input'){
 $('.remove-line-button').click()
; }



 }