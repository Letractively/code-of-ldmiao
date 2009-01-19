var sbAutoSaveService = {

	lastURL : "",

	init : function()
	{
		if ( !("newItem" in sbCommonUtils) )
		{
			setTimeout(function(){ alert("Please upgrade ScrapBook to 1.2 or later."); }, 1000);
			return;
		}
		gBrowser.addEventListener("load", function(aEvent){ sbAutoSaveService.handleBrowserLoad(aEvent); }, true);
	},

	handleBrowserLoad : function(aEvent)
	{
		if ( !sbCommonUtils.getBoolPref("scrapbook.autosave.enabled", true) ) return;
		var win = aEvent.originalTarget.defaultView;
		if ( win != win.top ) return;
		if ( win.location.href == this.lastURL ) return;
		if ( win.location.href.indexOf("http") != 0 ) return;
		var timeStamp = sbCommonUtils.getTimeStamp().substring(0,8) + "000000";
		var targetURI = "urn:scrapbook:item" + timeStamp;
		if ( !sbDataSource.exists(sbCommonUtils.RDF.GetResource(targetURI)) )
		{
			var fItem = sbCommonUtils.newItem(timeStamp);
			timeStamp.match(/^(\d{4})(\d{2})(\d{2})\d{6}$/);
			fItem.title = (new Date(parseInt(RegExp.$1, 10), parseInt(RegExp.$2, 10) - 1, parseInt(RegExp.$3, 10))).toLocaleDateString();
			fItem.type = "folder";
			var fRes = sbDataSource.addItem(fItem, "urn:scrapbook:root", 0);
			sbDataSource.createEmptySeq(fRes.Value);
		}
		var presetData = [
			null,
			null,
			{
				"images" : sbCommonUtils.getBoolPref("scrapbook.autosave.images", true),
				"styles" : sbCommonUtils.getBoolPref("scrapbook.autosave.styles", true),
				"script" : sbCommonUtils.getBoolPref("scrapbook.autosave.script", false),
			},
			null,
			null,
		];
		sbContentSaver.captureWindow(win, false, false, targetURI, 0, presetData, null);
		this.lastURL = win.location.href;
	},

};


window.addEventListener("load", sbAutoSaveService.init, false);


