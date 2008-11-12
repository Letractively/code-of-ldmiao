/* ***** BEGIN LICENSE BLOCK *****
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1
 *
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 *
 * The Original Code is Easy DragToGo code.
 *
 * The Initial Developer of the Original Code is Sunwan.
 * Portions created by the Initial Developer are Copyright (C) 2008
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 *   Sunwan <SunwanCN@gmail.com>
 *
 * Alternatively, the contents of this file may be used under the terms of
 * either of the GNU General Public License Version 2 or later (the "GPL"),
 * or the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
 * in which case the provisions of the GPL or the LGPL are applicable instead
 * of those above. If you wish to allow use of your version of this file only
 * under the terms of either the GPL or the LGPL, and not to allow others to
 * use your version of this file under the terms of the MPL, indicate your
 * decision by deleting the provisions above and replace them with the notice
 * and other provisions required by the GPL or the LGPL. If you do not delete
 * the provisions above, a recipient may use your version of this file under
 * the terms of any one of the MPL, the GPL or the LGPL.
 *
 * ***** END LICENSE BLOCK ***** */

var easyDragToGo = {

  loaded: false,
  moving: false,
  StartAlready: false,
  onStartEvent: null,       // drag start event
  onDropEvent: null,        // drag drop event
  aXferData: null,          // drag data
  aDragSession: null,       // drag session
  timeId: null,

  onLoad: function() {
    if (!easyDragToGo.loaded) {
      var contentArea = getBrowser().mPanelContainer;
      if (contentArea) {
        eval("nsDragAndDrop.dragOver =" + nsDragAndDrop.dragOver.toString().replace(
          'aEvent.stopPropagation();',
          'if ( !easyDragToGo.moving ) { $& }')
        );
        eval("nsDragAndDrop.checkCanDrop =" + nsDragAndDrop.checkCanDrop.toString().replace(
          'if ("canDrop" in aDragDropObserver)',
          'if (easyDragToGo.StartAlready) this.mDragSession.canDrop = true; $&')
        );
        contentArea.addEventListener('draggesture', function(e) {easyDragToGo.dragStart(e)}, true);
        contentArea.addEventListener('dragover', function(e) {
            easyDragToGo.moving = true;
            nsDragAndDrop.dragOver(e, easyDragToGoDNDObserver);
            easyDragToGo.moving = false;
          }, false);
        contentArea.addEventListener('dragdrop', function(e) {
            nsDragAndDrop.drop(e, easyDragToGoDNDObserver);
          }, false);
      }
      easyDragToGo.loaded = true;
    }
  },

  dragStart: function(aEvent) {
    this.onStartEvent = aEvent;
    this.StartAlready = true;
    this.setTimeout();
  },

  clean: function() {
    this.StartAlready = false;
    if (this.onDropEvent) {
      this.onDropEvent.preventDefault();
      this.onDropEvent.stopPropagation();
    }
    this.onStartEvent = this.onDropEvent = this.aXferData = this.aDragSession = null;
  },

  setTimeout: function() {
    var timeout = easyDragUtils.getPref("timeout", 0);
    if (timeout > 0) {
      clearTimeout(this.timeId);
      this.timeId = setTimeout(function(){easyDragToGo.clean()}, timeout);
    }
  },

  openURL: function(aURI, src, target, X, Y) {
    if (!aURI) return;

    var act = "";

    if (target.indexOf("fromContentOuter") == -1) {

      var actionSets = easyDragUtils.getPref(target + ".actionSets", "|");

      if (!actionSets || actionSets == "|") return;

      var dir;
      var directions = actionSets.split('|')[0];

      switch (directions) {
        case "A":
          // any direction
          dir = "A";
          break;
        case "UD":
          // up and down
          dir = (Y > 0) ? "D" : "U";
          break;
        case "RL":
          // right and left
          dir = (X > 0) ? "R" : "L";
          break;
        case "RLUD":
          // right left up down
          if ( X > Y )
            ( X + Y > 0 ) ? (dir = "R") : (dir = "U");
          else
            ( X + Y > 0 ) ? (dir = "D") : (dir = "L");
          break;
        default:
          return;
      }

      var re = new RegExp(dir + ':(.+?)(\\s+[ARLUD]:|$)', '');
      try { if ( re.test(actionSets) ) act = RegExp.$1; } catch(e) {}
    }
    else {
      act = easyDragUtils.getPref(target, "link-fg");
    }

    if (!act) return;

    var browser = getTopWin().getBrowser();
    var uri = "";
    var bg = true;
    var postData = {};

    // get search strings
    if ((target == "text" || target == "fromContentOuter.text") && act.indexOf("search-") == 0) {
      var submission = this.getSearchSubmission(aURI, act);
      if (submission) {
        uri = submission.uri.spec;
        postData.value = submission.postData;
        if (uri && /(fg|bg|cur)$/.test(act))
          act = "search-" + RegExp.$1;
        else
          act = "";
      }
      else
        act = "";
      if (!act) alert("No Search Engines!");
    }

    switch (act) {
      case "search-fg":
      case "link-fg":
        // open a new tab and selected it
        bg = false;
      case "search-bg":
      case "link-bg":
        if (!uri) uri = getShortcutOrURI(aURI, postData);
        try {
          var cur = (!bg || browser.mTabs.length == 1) &&
                browser.webNavigation.currentURI.spec == "about:blank" &&
                !browser.mCurrentBrowser.webProgress.isLoadingDocument ||
                (/^(javascript|mailto):/i.test(uri));
        } catch(e) {}
        if (cur)
          // open in current tab
          loadURI(uri, null, postData.value, true);
        else
          // open a new tab
          browser.loadOneTab(uri, null, null, postData.value, bg, true);
        break;

      case "search-cur":
      case "link-cur":
        // open in current
        if (!uri) uri = getShortcutOrURI(aURI, postData);
        loadURI(uri, null, postData.value, true);
        break;

      case "save-link":
        // save links as...
        saveURL(aURI, null, null, true, false, browser.currentURI);
        break;

      case "img-fg":
        // open imgs in new tab and selected it
        bg = false;
      case "img-bg":
        // open imgs in new tab in background
        browser.loadOneTab(src, null, null, null, bg);
        break;

      case "img-cur":
        // open imgs in current
        loadURI(src, null, null, false);
        break;

      case "save-img":
        // save imgs as...
        saveImageURL(src, null, null, false, false, browser.currentURI);
        break;

      case "save-df-img":
        // direct save imgs to folder
        var err = this.saveimg(src);
        if (err) alert("Saving image failed: " + err);
        break;

      default:
        // for custom
        if (/^custom#(.+)/.test(act)) {
          var custom = RegExp.$1;
          if (custom) {
            var code = easyDragUtils.getPref("custom." + custom, "return");
            if (code) {
              try {
                this.customCode(code, aURI, src, target, X, Y);
              }
              catch(e) {
                alert("Easy DragToGo: Custom(" + custom + ") Error: " + e + "\n");
              }
            }
          }
        }
        // do nothing
        break;
    }
  },

  customCode: function(code, url, src, target, X, Y) {
    eval(code);
  },

  getSearchSubmission: function(searchStr, action) {
    try {
      var ss = Components.classes["@mozilla.org/browser/search-service;1"]
                .getService(Components.interfaces.nsIBrowserSearchService);
      var engine, engineName;
      if ( /^search-(.+?)-?(fg|bg|cur)$/.test(action) )
        engineName = RegExp.$1;
      else
        engineName = "c";

      if ( engineName == "c" )
        engine = ss.currentEngine || ss.defaultEngine;
      else if ( engineName == "d" )
        engine = ss.defaultEngine || ss.currentEngine;
      else {
        engine = ss.getEngineByName(engineName);
        if (!engine) engine = ss.currentEngine || ss.defaultEngine;
      }
      return engine.getSubmission(searchStr, null);
    }
    catch (e) {
      return null;
    }
  },

  saveimg: function(aSrc) {
    if (!aSrc) return "No Src!";

    if ( /^file\:\/\/\//.test(aSrc) ) return "Local image, does not need save!";

    var path = easyDragUtils.getDownloadFolder();
    var fileName;

    try {
      var imageCache = Components.classes['@mozilla.org/image/cache;1'].getService(imgICache);
      var props = imageCache.findEntryProperties(makeURI(aSrc, getCharsetforSave(null)));
      if (props)
        fileName = props.get("content-disposition", nsISupportsCString).toString().
                   replace(/^.*?filename=(["']?)(.+)\1$/, '$2');
    } catch (e) {}

    if (!fileName) fileName = aSrc.substr( aSrc.lastIndexOf('/') + 1 );
    if (fileName) fileName = fileName.replace(/\?.*/, "").replace(/[\\\/\*\|:"<>]/g, "-");
    if (!fileName) return "No image!";
    
    var currentTime = new Date().getTime();
    fileName = currentTime+'_'+fileName;
    
    var fileSaving = Components.classes["@mozilla.org/file/local;1"].
                     createInstance(Components.interfaces.nsILocalFile);
    fileSaving.initWithPath(path);
    if ( !fileSaving.exists() || !fileSaving.isDirectory() )
      return "The download folder does not exist!";

    // create a subdirectory with the domain name of current page
    if ( easyDragUtils.getPref("saveDomainName", true) ) {
      var domainName = getTopWin().getBrowser().currentURI.host;
      if (domainName) {
        fileSaving.append(domainName);
        if ( !fileSaving.exists() || !fileSaving.isDirectory() ) {
          try {
            fileSaving.create(1, 0755); // 1: DIRECTORY_TYPE
          }
          catch(e) {
            return "Create directory failed!";
          }
        }
        path = fileSaving.path;
      }
    }

    fileSaving.append(fileName);

    // does not overwrite the original file
    var newFileName = fileName;
    while ( fileSaving.exists() ) {
      if ( newFileName.indexOf('.') != -1 ) {
        var ext = newFileName.substr(newFileName.lastIndexOf('.'));
        var file = newFileName.substring(0, newFileName.length - ext.length);
        newFileName = this.getAnotherName(file) + ext;
      }
      else
        newFileName = this.getAnotherName(newFileName);
      fileSaving.initWithPath(path);
      fileSaving.append(newFileName);
    }

    var cacheKey  = Components.classes['@mozilla.org/supports-string;1'].
                    createInstance(Components.interfaces.nsISupportsString);
    cacheKey.data = aSrc;

    var urifix  = Components.classes['@mozilla.org/docshell/urifixup;1'].
                  getService(Components.interfaces.nsIURIFixup);
    var uri     = urifix.createFixupURI(aSrc, 0);
    var hosturi = null;
    if ( uri.host.length > 0 )
      hosturi = urifix.createFixupURI(uri.host, 0);

    var persist = Components.classes['@mozilla.org/embedding/browser/nsWebBrowserPersist;1'].
                  createInstance(Components.interfaces.nsIWebBrowserPersist);
    persist.persistFlags = Components.interfaces.nsIWebBrowserPersist.PERSIST_FLAGS_FROM_CACHE |
                           Components.interfaces.nsIWebBrowserPersist.PERSIST_FLAGS_CLEANUP_ON_FAILURE;
    persist.saveURI(uri, cacheKey, hosturi, null, null, fileSaving);
    if (persist.result) return "Can not save image or get image failed!";

    function StatusLabel() {
      var SaveLabel = "The image(" + newFileName + ") has been saved to "+ path;
      document.getElementById('statusbar-display').label = SaveLabel;
    }
    setTimeout(StatusLabel,100);
    return 0;
  },

  // filenameNoExt -> filenameNoExt[1] -> filenameNoExt[2] ...
  getAnotherName: function(fName) {
    if ( /\[(\d+)\]$/.test(fName) ) {
      var i = 1 + parseInt(RegExp.$1);
      fName = fName.replace(/\[\d+\]$/, "[" + i + "]");
    }
    else
      fName += "[1]";
    return fName;
  },

  SelectedText: function(node) {
    if (!node) return "";
    if ( node.localName == "TEXTAREA" || (node.localName == "INPUT" && node.type == "text") )
      return node.value.substring(node.selectionStart, node.selectionEnd);
    else
      return document.commandDispatcher.focusedWindow.getSelection().toString();
  },

  seemAsURL: function(url) {
      // url test
      var DomainName = /(\w+(\-+\w+)*\.)+\w{2,7}/;
      var HasSpace = /\S\s+\S/;
      var KnowNameOrSlash = /^(www|bbs|forum|blog)|\//;
      var KnowTopDomain1 = /\.(com|net|org|gov|edu|info|mobi|mil|asia)$/;
      var KnowTopDomain2 = /\.(de|uk|eu|nl|it|cn|be|us|br|jp|ch|fr|at|se|es|cz|pt|ca|ru|hk|tw|pl)$/;
      var IsIpAddress = /^([1-2]?\d?\d\.){3}[1-2]?\d?\d/;
      var seemAsURL = !HasSpace.test(url) && DomainName.test(url) &&
                       (KnowNameOrSlash.test(url) || KnowTopDomain1.test(url) ||
                        KnowTopDomain2.test(url) || IsIpAddress.test(url));
      return seemAsURL;
  },

  getForceURL: function(url) {
    var code;
    var str = "";
    url = url.replace(/\s|\r|\n|\u3000/g, "");
    for (var i = 0; i < url.length; i++) {
      code = url.charCodeAt(i);
      if (code >= 65281 && code <= 65373)
        str += String.fromCharCode(code - 65248);
      else
        str += url.charAt(i);
    }
    str = this.fixupSchemer(str);
    str = this.SecurityCheckURL(str);
    return str;
  },

  SecurityCheckURL: function(aURI) {
    if ( /^data:/.test(aURI) ) return "";
    if ( /^javascript:/.test(aURI) ) return aURI;
    var sourceURL = getBrowser().currentURI.spec;
    const nsIScriptSecurityManager = Components.interfaces.nsIScriptSecurityManager;
    var secMan = Components.classes["@mozilla.org/scriptsecuritymanager;1"]
                  .getService(nsIScriptSecurityManager);
    const nsIScriptSecMan = Components.interfaces.nsIScriptSecurityManager;
    try {
      secMan.checkLoadURIStr(sourceURL, aURI, nsIScriptSecMan.STANDARD);
    } catch(e) {
      aURI = "";
    }
    return aURI;
  },

  fixupSchemer: function(aURI) {
    if ( /^(?::\/\/|\/\/|\/)?(([1-2]?\d?\d\.){3}[1-2]?\d?\d(\/.*)?|[a-z]+[a-z\d]+\.[a-z\d\.]+(\/.*)?)$/i.test(aURI) )
      aURI = "http://" + RegExp.$1;
    else if ( /^\w+[\-\.\w]*@(\w+(\-+\w+)*\.)+\w{2,7}$/.test(aURI) )
      aURI = "mailto:" + aURI;
    else {
      var table = "ttp=>http,tp=>http,p=>http,ttps=>https,tps=>https,ps=>https,s=>https";
      var regexp = new RegExp();
      if (aURI.match(regexp.compile('^('+ table.replace(/=>[^,]+|=>[^,]+$/g, '').replace(/\s*,\s*/g, '|')+'):', 'g'))) {
        var target = RegExp.$1;
        table.match(regexp.compile('(,|^)'+target+'=>([^,]+)'));
        aURI = aURI.replace(target, RegExp.$2);
      }
    }
    return aURI;
  }
}; 

var easyDragToGoDNDObserver = {

  onDragOver: function(aEvent, aFlavour, aDragSession) {
    aDragSession.canDrop = true;
    // for drag tabs or bookmarks
    if (!easyDragToGo.StartAlready) {
      easyDragToGo.onStartEvent = aEvent;
      easyDragToGo.StartAlready = true;
      easyDragToGo.setTimeout();
    }
  },

  onDrop: function(aEvent, aXferData, aDragSession) {
    if (!easyDragToGo.StartAlready) return;
    easyDragToGo.onDropEvent = aEvent;
    easyDragToGo.aXferData = aXferData;
    easyDragToGo.aDragSession = aDragSession;

    var sNode = aDragSession.sourceNode;
    var url;
    if ( !sNode ) {
      // Drag and Drop from content outer
      try {url = aXferData.data.replace( /^[\s\n]+|[\s\n]+$/g, '' )} catch(e) {}
      if (!url) {
        easyDragToGo.clean();
        return;
      }
      var target = "fromContentOuter.text";
      if ( easyDragToGo.seemAsURL(url) || (/^file:\/\/\/[\S]+$/.test(url)) ) {
        //force it to a url or local file/directory
        if ( /^file:\/\/\//.test(url)) {
          if ( /([^\/]+\.(xpi|jar))$/.test(url) ) {
            eval("InstallTrigger.install({ '" + RegExp.$1 + "' : url })");
            easyDragToGo.clean();
            return;
          }
          else
            target = "fromContentOuter.link";
        }
        else {
          var tmpurl = url;
          url = easyDragToGo.fixupSchemer(url);
          url = easyDragToGo.SecurityCheckURL(url);
          if (url)
            target = "fromContentOuter.link";
          else
            url = tmpurl;
        }
      }
      easyDragToGo.openURL(url, null, target);
    }
    else {
      // Drag and Drop from Content area
      var relX = aEvent.screenX - easyDragToGo.onStartEvent.screenX;
      var relY = aEvent.screenY - easyDragToGo.onStartEvent.screenY;
      // do nothing with drag distance less than 10px
      if ( Math.abs(relX) < 10 && Math.abs(relY) < 10 ) {
        easyDragToGo.clean();
        return;
      }

      var str, src;
      var selectStr =  "";
      var type = "STRING"; 
      var target = "link";

      url = str = aXferData.data;

      try {
        selectStr = easyDragToGo.SelectedText(easyDragToGo.onStartEvent.target);
        selectStr = selectStr.replace( /\r\n/g, "\n").replace( /\r/g, "\n");
      } catch(e) {}

      if (str != selectStr) {
        var idx = str.indexOf("\n");
        if (idx > 0) {
          url = str.substr(0, idx);
          str = str.substr(idx + 1);
        }
        if (str == selectStr)
          url = str;
        else if ( !(/\s|\n/.test(url)) && (/^([a-z]{2,7}:\/\/|mailto:|about:|javascript:)/i.test(url)) )
          type = "URL";
        else
          url = selectStr;
      }

      url = url.replace( /^[\s\n]+|[\s\n]+$/g, '' );

      if ( url && type == "URL" ) {

        src = url = easyDragToGo.SecurityCheckURL(url);

        if (sNode.nodeName == "IMG") {
          src = sNode.src;
          target = "img";
        }
        else if (aEvent.ctrlKey) {
          // as text with ctrlkey
          var aNode = easyDragToGo.onStartEvent.target;
          while (aNode && aNode.nodeName != "A") aNode = aNode.parentNode;
          if (aNode && aNode.textContent) {
            url = aNode.textContent;
            target = "text";
          }
        }
      }
      else if (url) {
        var tmpurl = url;
        if (aEvent.ctrlKey) {
          url = easyDragToGo.getForceURL(url)    // force convert to a url
          if (url)
            target = "link";
          else
            url = tmpurl;
        }
        else if ( easyDragToGo.seemAsURL(url) ) { //seem as a url
          url = easyDragToGo.fixupSchemer(url);
          url = easyDragToGo.SecurityCheckURL(url);
          if (!url) { // not a url, search it
            url = tmpurl;
            target = "text";
          }
        }
        else         //it's a text string, so search it
          target = "text";
      }

      easyDragToGo.openURL(url, src, target, relX, relY);
    }

    easyDragToGo.clean();
  },

  getSupportedFlavours: function() {
    var flavourSet = new FlavourSet();
    flavourSet.appendFlavour("text/x-moz-url");
    flavourSet.appendFlavour("text/unicode");
    return flavourSet;
  }
};

window.addEventListener('load', easyDragToGo.onLoad, false);
