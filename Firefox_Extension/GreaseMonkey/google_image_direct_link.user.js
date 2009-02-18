/*
    Rewrite Google Image Search result
    links to point directly at the images
    Patrick Cavit, pcavit@gmail.com
    http://patcavit.com

    Copy, use, modify, spread as you see fit.
    Massive thanks go out to Eric Hamiter, this code
    is just a quick modification of his extesion at
    http://roachfiend.com/
*/

/*
    Modified by Juhani Naskali
    Thanks go out to Patrick Cavit for the original script
    and FurYy for the hack with the original google links.
*/

// ==UserScript==
// @name          Google Image direct links
// @namespace     http://juhani.naskali.net/files/gm/
// @description   Rewrites Google Image Search links to point straight to the pictures, and adds links to the corresponding websites without google frames.
// @version	0.1
// @date		2007-04-15
// @include       http://images.google.*/*
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

    function directGoogleImageLinks(realimage){
        doc = window.document;

        // Get a list of all A tags that have an href attribute containing the start and stop key strings.
        var googLinks = selectNodes(doc, doc.body, "//A[contains(@href,'/imgres?imgurl=')][contains(@href,'&imgrefurl=')]");
           
        // MOD: links the domain name to the original google link
        var googFonts = selectNodes(doc, doc.body, "//FONT[contains(@color,'#008000')]");
        
        var imgs = selectNodes(doc, doc.body, "//IMG[contains(@src, '/images?q=')]");
        
        //alert("googLinks:"+googLinks.length+" ,googFonts:"+googFonts.length+" ,imgs:"+imgs.length);
        
        for (var x=0; x<googLinks.length; x++)
        {
            // Capture the stuff between the start and stop key strings.
            var gmatch = googLinks[x].href.match( /\/imgres\?imgurl\=(.*?)\&imgrefurl\=/ );
            var urlmatch = googLinks[x].href.match( /\&imgrefurl\=(.*?)\&h\=/ );
            
            // If it matched successfully...
            if (gmatch)
            {
                if(realimage!=undefined){
                    // Replace the domain name with link to the webpage containing the image.
                    googFonts[x].innerHTML="<a href=\""+decodeURIComponent(urlmatch[1])+"\">"+googFonts[x].innerHTML+"</a>";
                    
                    //googFonts[x].innerHTML="<a href=\""+decodeURI(gmatch[1])+"\">"+googFonts[x].innerHTML+"</a>";
                    
                    // Replace the link's href with the contents of the text captured in the regular expression's parenthesis.
                    //googLinks[x].href = decodeURI(gmatch[1]);
                } else {
                    googLinks[x].href = decodeURI(gmatch[1]);
                    
					width=imgs[x].width;
					height=imgs[x].height;
					imgs[x].src = decodeURI(gmatch[1]);
					imgs[x].width = width;
					imgs[x].height = height;
					//alert(imgs[x].width+","+imgs[x].height);
				}
            }
        }
    }
    
	directGoogleImageLinks(1);
	
	GM_registerMenuCommand("RealGoogleImage", directGoogleImageLinks);
})();


