// ==UserScript==
// @name          Baidu Image direct links
// @namespace     http://demiao-lin.appspot.com/
// @description   Rewrites Baidu Image Search links to point straight to the pictures, and adds links to the corresponding websites without Baidu frames.
// @version	0.1
// @date		2008-05-15
// @include       http://image*.baidu.com/*
// @include       http://image*.baidu.jp/*
// ==/UserScript==

(function()
{
    function selectNodes(doc, context, xpath)
    {
       var nodes = doc.evaluate(xpath, context, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
       var result = new Array( nodes.snapshotLength );
	   
       for (var x=0; x<result.length; x++)
       {
          result[x] = nodes.snapshotItem(x);
       }
	   
       return result;
    }
	
	function directBaiduImageLinks(realimage)
	{
		//alert("realimage:"+realimage);
		
	    doc = window.document;
		
	    // Get a list of all A tags that have an href attribute containing the start and stop key strings.
	    var baiduLinks = selectNodes(doc, doc.body, "//A[contains(@href,'/i?ct=')][contains(@href,'&tn=baiduimagedetail') or contains(@href,'&tn=baiduimagenewsdetail')]");
		var imgLinks = selectNodes(doc, doc.body, "//A[contains(@href,'/ir?t=')]");
		
		var imgs = selectNodes(doc, doc.body, "//img[contains(@src, '/it/u=') or contains(@src, '/it?u=')]");
	    
		//alert(baiduLinks.length+","+imgLinks.length);

	    for (var x=0; x<imgLinks.length; x++)
	    {
	        // Capture the stuff between the start and stop key strings.
	        var gmatch = imgLinks[x].href.match( /\/ir\?t\=.*?\&u\=(.*?)\&f\=/ );
			
	        // If it matched successfully...
	        if (gmatch)
	        {
				if(realimage!=undefined){
					//alert("gmatch[1]:"+gmatch[1]);
					//alert("imgLinks["+x+"].href:"+imgLinks[x].href+", gmatch[1]:"+gmatch[1]);
					//decodeURI(gmatch[1]);
					baiduLinks[x].href = gmatch[1];
				} else {
					width=imgs[x].width;
					height=imgs[x].height;
					imgs[x].src = gmatch[1];
					imgs[x].width = width;
					imgs[x].height = height;
					//alert(imgs[x].width+","+imgs[x].height);
				}
	        }
	    }
	}
	
	directBaiduImageLinks(1);
	
	GM_registerMenuCommand("RealBaiduImage", directBaiduImageLinks);
	
})();


