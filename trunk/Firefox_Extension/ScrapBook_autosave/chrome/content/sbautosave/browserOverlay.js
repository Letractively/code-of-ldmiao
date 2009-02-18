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
        
        var href = win.location.href;
        if(href.indexOf('http://')!=0 && href.indexOf('https://')!=0 && href.indexOf('file://')!=0 && href.indexOf('ftp://')!=0){
            return;
        }
        if(!sbAutoSaveService.isIncludedPages(href)){
            return;
        }
        
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
    isIncludedPages: function(href) {
        var includedpages_enabled = sbAutoSaveService.getPref('scrapbook.autosave.includeRulesEnabled');
        if(includedpages_enabled) {
            var includedpages = sbAutoSaveService.getPref('scrapbook.autosave.includeRules');
            var includedpagesArray = includedpages.split('\n');
            //alert(includedpagesArray.length)
            for(var i=0; i<includedpagesArray.length; i++) {
                var includedpage = includedpagesArray[i];
                var pattern = new RegExp(includedpage, 'i');
                if(pattern.test(href)) {
                    return true;
                }
            }
            return false;
        } else {
            return true;
        }
    },
    
    //*******************************************************************************************//
    getPref: function(name) {
        var prefs = Components.classes['@mozilla.org/preferences-service;1'].getService(Components.interfaces.nsIPrefService);
        var prefs = prefs.getBranch('extensions.hpassistant.');
        
        if(prefs.getPrefType(name)==prefs.PREF_STRING) {
            return prefs.getCharPref(name);
        } else if(prefs.getPrefType(name)==prefs.PREF_INT) {
            return prefs.getIntPref(name);
        } else if(prefs.getPrefType(name)==prefs.PREF_BOOL) {
            return prefs.getBoolPref(name);
        } else {
            return null;
        }
    },
    
    setPref: function(name, value) {
        var prefs = Components.classes['@mozilla.org/preferences-service;1'].getService(Components.interfaces.nsIPrefService);
        var prefs = prefs.getBranch('extensions.hpassistant.');
        
        if(typeof value == 'string') {
            prefs.setCharPref(name, value);
        } else if(typeof value == 'number') {
            prefs.setIntPref(name, value);
        } else if(typeof value == 'boolean') {
            prefs.setBoolPref(name, value);
        } else {
            prefs.setComplexValue(name, value);
        }
    },

};


window.addEventListener("load", sbAutoSaveService.init, false);


