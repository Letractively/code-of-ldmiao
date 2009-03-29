/**
 *
 * www.FLABELL.com
 * New Flash Components Every Week!
 *
 *
 * Flash Mp3 Player v1.0 (03/23/2009) <http://www.flabell.com/>
 * 
 * Copyright (c) 2009 Vuzum Media <http://www.vuzum.com/>
 * For information about licencing, please visit <http://www.flabell.com/terms>
 *
 *
 * email: support@flabell.com
 *
 */

import mx.utils.*
import caurina.*;

import com.vuzum.utils.*;
import com.vuzum.*;

class com.vuzum.Main extends MovieClip
{
    // STATIC VARS
    private static var instance : Main;

    // COMPONENTS INSIDE
    public var mcBackground : MovieClip;
    public var mcAlbums : MovieClip;
    public var mcMask : MovieClip;
    
    private var sWidth : Number;
    private var sHeight : Number;
    private var settingsData : XML;
    private var pathTo : String;
    private var settingsPath : String;
    /** 
     * @return singleton instance of Main
     */
    public static function getInstance() : Main 
    {
        if (instance == null) 
        {
            new Main();
        }
        return instance;
    }

    /**
     * Main constructor
     */
    public function Main() 
    {
        instance = this;
        new Prototypes();
        initPage();
        
        //trace("MAIN");
    }
    
    /**
     * initialize the page
     */
    private function initPage():Void
    {
    	Stage.align = "TL";
		Stage.scaleMode = "noScale";
		Stage.showMenu = false;
		
		pathTo = String(_root.pathToFiles);
		
		if(pathTo == "undefined" || pathTo == undefined)
		{
			pathTo = "player";
		}
		
		settingsPath = pathTo + "/" + _root.settingsPath;
		if(isNaN(settingsPath)) settingsPath = pathTo + "/" + "xml/settings.xml";
		
		loadSettingsData(settingsPath);
    }
    
    /**
	 * load settings xml file
	 */
	private function loadSettingsData(str : String) : Void
	{
		settingsData = new XML();
		settingsData.ignoreWhite = true;
		settingsData.load(str);
		settingsData.onLoad = Proxy.create(this, xmlOnLoad);
	}
	
	private function xmlOnLoad(success : Boolean) : Void
	{
		if(success)
		{
			if(_root.stageW != undefined)
			{
				sWidth = Number(_root.stageW);
			}
			else
			{
				sWidth = (settingsData.firstChild.childNodes[27].attributes.width != undefined) ? Number(settingsData.firstChild.childNodes[27].attributes.width) : Stage.width;
			}
			
			if(_root.stageH != undefined)
			{
				sHeight = Number(_root.stageH);
			}
			else
			{
				sHeight = (settingsData.firstChild.childNodes[27].attributes.height != undefined) ? Number(settingsData.firstChild.childNodes[27].attributes.height) : Stage.height;
			}
			
			
			//background for player
			mcBackground = this.createEmptyMovieClip("mcBackground", this.getNextHighestDepth());
			mcBackground.attachMovie("mcBackgroundColor", "mcBackgroundColor", mcBackground.getNextHighestDepth());
			mcBackground._width = sWidth;
			mcBackground._height = sHeight;
			
			mcMask = this.createEmptyMovieClip("mcMask", this.getNextHighestDepth());
			mcMask._alpha = 0;
			mcMask.attachMovie("mcBackgroundColor", "mcBackgroundColor", mcMask.getNextHighestDepth());
			mcMask._width = sWidth;
			mcMask._height = sHeight;
			
			//create albums movie
			mcAlbums = this.attachMovie("mcAlbums", "mcAlbums", this.getNextHighestDepth());
	        mcAlbums._x = 0;
	        mcAlbums.setMask(mcMask);
	        
			mcAlbums.initAlbums();
		}
	}
}