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
import flash.geom.Rectangle;
import com.vuzum.Main;

class com.vuzum.ScrollBar extends MovieClip 
{
	private var mcBg : MovieClip;
	private var mcScrollBg : MovieClip;
	private var mcScrollBtn : MovieClip;
	private var mcContent : MovieClip;
	private var mcMask : MovieClip;
	private var mcControl : MovieClip;
	private var mcPlay : MovieClip;
	private var mcPause : MovieClip;
	public var autoscrollTimeout : Number;
	
	private var grid : Rectangle;
	private var direction : Boolean;
	
	private var maxWidth : Number;
	private var maxHeight : Number;
	private var changeDirection : Boolean;
	private var border : Number = 10;
	
	private var flag : Boolean;
	
	private var pauseLength : Number = 50;
	public var isPlaying : Boolean;
	public var releaseBgTimeout : Number;
	
	/*
	 * constructor
	 */
	public function ScrollBar()
	{
		grid = new Rectangle(5, 2, 290, 1);
		changeDirection = false;
		flag = true;
	}
	
	/**
	 * init scroll bar function with variables from settings XML file
	 */
	public function init(contentMC : MovieClip, maskMC : MovieClip, pWidth : Number, pHeight : Number, bDirection : Boolean, btnHeight : Number, bgHeight : Number, bgLarge : Number, btnBeginColor : Number, btnEndColor : Number, bgBeginColor : Number, bgMiddleColor : Number, bgEndColor : Number, largeBgBeginColor : Number, largeBgEndColor : Number, scrollbarControlLinesColor : Number, scrollbarControlBeginColor : Number, scrollbarControlEndColor : Number, scrollBgLargeStroke : Number, scrollBgStroke : Number) : Void
	{
		mcContent = contentMC;
		mcMask = maskMC;
		direction = bDirection;
		
		var boxPropertiesBgLarge:Object = {x:0, y:0, w:2, h:2}; // x and y defining x and y positions, w and h defining width and height of your box
		var colArrayBgLarge:Array = [largeBgBeginColor, largeBgEndColor]; // your colors
		var alpArrayBgLarge:Array = [100, 100]; // your alphas
		var sprArrayBgLarge:Array = [0, 255]; // gradient spread
		var matrixDataBgLarge:Object = {matrixType:"box", x:0, y:0, w:2, h:2, r:90/180*Math.PI};
		
		mcBg.lineStyle(0.25, scrollBgLargeStroke);
		with (mcBg) 
		{ 
			// yourMovieClipInstance is the instance of movie clip you wish to draw to
			moveTo(boxPropertiesBgLarge.x, boxPropertiesBgLarge.y);
			beginGradientFill("linear", colArrayBgLarge, alpArrayBgLarge, sprArrayBgLarge, matrixDataBgLarge);
			lineTo(boxPropertiesBgLarge.x + boxPropertiesBgLarge.w, boxPropertiesBgLarge.y);
			lineTo(boxPropertiesBgLarge.x + boxPropertiesBgLarge.w, boxPropertiesBgLarge.y + boxPropertiesBgLarge.h);
			lineTo(boxPropertiesBgLarge.x, boxPropertiesBgLarge.y + boxPropertiesBgLarge.h);
			lineTo(boxPropertiesBgLarge.x, boxPropertiesBgLarge.y);
			endFill();
		}
		
		mcControl.lineStyle(0.25, scrollBgLargeStroke);
		with (mcControl) 
		{ 
			// yourMovieClipInstance is the instance of movie clip you wish to draw to
			moveTo(boxPropertiesBgLarge.x, boxPropertiesBgLarge.y);
			beginGradientFill("linear", colArrayBgLarge, alpArrayBgLarge, sprArrayBgLarge, matrixDataBgLarge);
			lineTo(boxPropertiesBgLarge.x + boxPropertiesBgLarge.w, boxPropertiesBgLarge.y);
			lineTo(boxPropertiesBgLarge.x + boxPropertiesBgLarge.w, boxPropertiesBgLarge.y + boxPropertiesBgLarge.h);
			lineTo(boxPropertiesBgLarge.x, boxPropertiesBgLarge.y + boxPropertiesBgLarge.h);
			lineTo(boxPropertiesBgLarge.x, boxPropertiesBgLarge.y);
			endFill();
		}
		
		
		var boxPropertiesBtn:Object = {x:0, y:0, w:2, h:2}; // x and y defining x and y positions, w and h defining width and height of your box
		var colArrayBtn:Array = [btnBeginColor, btnEndColor]; // your colors
		var alpArrayBtn:Array = [100, 100]; // your alphas
		var sprArrayBtn:Array = [0, 255]; // gradient spread
		var matrixDataBtn:Object = {matrixType:"box", x:0, y:0, w:2, h:2, r:0};

		with (mcScrollBtn) 
		{ 
			// yourMovieClipInstance is the instance of movie clip you wish to draw to
			moveTo(boxPropertiesBtn.x, boxPropertiesBtn.y);
			beginGradientFill("linear", colArrayBtn, alpArrayBtn, sprArrayBtn, matrixDataBtn);
			lineTo(boxPropertiesBtn.x + boxPropertiesBtn.w, boxPropertiesBtn.y);
			lineTo(boxPropertiesBtn.x + boxPropertiesBtn.w, boxPropertiesBtn.y + boxPropertiesBtn.h);
			lineTo(boxPropertiesBtn.x, boxPropertiesBtn.y + boxPropertiesBtn.h);
			lineTo(boxPropertiesBtn.x, boxPropertiesBtn.y);
			endFill();
		}
		
		var boxPropertiesBg:Object = {x:0, y:0, w:pWidth - 2* border - pauseLength, h:2}; // x and y defining x and y positions, w and h defining width and height of your box
		var colArrayBg:Array = [bgBeginColor, bgMiddleColor, bgEndColor]; // your colors
		var alpArrayBg:Array = [100, 100, 100]; // your alphas
		var sprArrayBg:Array = [0, 123, 255]; // gradient spread
		var matrixDataBg:Object = {matrixType:"box", x:0, y:0, w:pWidth - 2* border - pauseLength, h:2, r:90/180*Math.PI};
		
		mcScrollBg.lineStyle(0.25, scrollBgStroke);
		with (mcScrollBg) 
		{ 
			// yourMovieClipInstance is the instance of movie clip you wish to draw to
			moveTo(boxPropertiesBg.x, boxPropertiesBg.y);
			beginGradientFill("linear", colArrayBg, alpArrayBg, sprArrayBg, matrixDataBg);
			lineTo(boxPropertiesBg.x + boxPropertiesBg.w, boxPropertiesBg.y);
			lineTo(boxPropertiesBg.x + boxPropertiesBg.w, boxPropertiesBg.y + boxPropertiesBg.h);
			lineTo(boxPropertiesBg.x, boxPropertiesBg.y + boxPropertiesBg.h);
			lineTo(boxPropertiesBg.x, boxPropertiesBg.y);
			endFill();
		}
		
		mcBg._height = bgLarge;
		mcScrollBg._height = bgHeight;
		mcScrollBtn._height = btnHeight;
		
		
		mcBg._width = pWidth - pauseLength;
		//mcScrollBg._width = pWidth - 2* border - pauseLength;
		mcScrollBg._x = border;
		mcScrollBg._y = Math.round((mcBg._height - mcScrollBg._height)/2);
		mcScrollBtn._width = pWidth - pauseLength;
		mcScrollBtn._x = border;
		mcScrollBtn._y = Math.round((mcBg._height - mcScrollBtn._height)/2);
		
		mcControl._height = bgLarge;
		mcControl._width = pauseLength;
		mcControl._x = mcBg._width;
		
		if(direction == true)
		{
			mcScrollBg._x = border;
			mcScrollBtn._x = border;
			mcScrollBtn._width = (maskMC._width * mcScrollBg._width)/contentMC._width;
		}
		else
		{
			mcScrollBg._y = border;
			mcScrollBtn._y = border;
			mcScrollBtn._height = (maskMC._height * mcScrollBg._height)/contentMC._height;
		}
		
		var boxPropertiesPlay:Object = {x:0, y:0, w:Math.round(bgLarge/2), h:Math.round(bgLarge/2)}; // x and y defining x and y positions, w and h defining width and height of your box
		var colArrayPlay:Array = [scrollbarControlBeginColor, scrollbarControlEndColor]; // your colors
		var alpArrayPlay:Array = [100, 100]; // your alphas
		var sprArrayPlay:Array = [0, 255]; // gradient spread
		var matrixDataPlay:Object = {matrixType:"box", x:0, y:0, w:Math.round(bgLarge/2), h:Math.round(bgLarge/2), r:90/180*Math.PI};
		
		mcPlay = this.createEmptyMovieClip("mcPlay", this.getNextHighestDepth());
		with (mcPlay) 
		{
			beginFill(0x000000, 0);
			lineTo(boxPropertiesPlay.x + boxPropertiesPlay.w, boxPropertiesPlay.y);
			lineTo(boxPropertiesPlay.x + boxPropertiesPlay.w, boxPropertiesPlay.y + boxPropertiesPlay.h);
			lineTo(boxPropertiesPlay.x, boxPropertiesPlay.y + boxPropertiesPlay.h);
			lineTo(boxPropertiesPlay.x, boxPropertiesPlay.y);
			endFill(); 
			// yourMovieClipInstance is the instance of movie clip you wish to draw to
			lineStyle(0.25, scrollbarControlLinesColor);
			moveTo(0, 0);
			
			beginGradientFill("linear", colArrayPlay, alpArrayPlay, sprArrayPlay, matrixDataPlay);
			lineTo(Math.round(bgLarge/2), Math.round(bgLarge/4));
			lineTo(0, Math.round(bgLarge/2));
			endFill();
		}
		mcPlay._x = Math.round(mcControl._x + mcControl._width/2 - mcPlay._width/2 + 3);
		mcPlay._y = Math.round(mcControl._y + mcControl._height/2 - mcPlay._height/2);
		
		mcPause = this.createEmptyMovieClip("mcPause", this.getNextHighestDepth());
		with (mcPause) 
		{ 
			beginFill(0x000000, 0);
			lineTo(boxPropertiesPlay.x + boxPropertiesPlay.w/2, boxPropertiesPlay.y);
			lineTo(boxPropertiesPlay.x + boxPropertiesPlay.w/2, boxPropertiesPlay.y + boxPropertiesPlay.h);
			lineTo(boxPropertiesPlay.x, boxPropertiesPlay.y + boxPropertiesPlay.h);
			lineTo(boxPropertiesPlay.x, boxPropertiesPlay.y);
			endFill();
			
			// yourMovieClipInstance is the instance of movie clip you wish to draw to
			lineStyle(0.25, scrollbarControlLinesColor);
			beginGradientFill("linear", colArrayPlay, alpArrayPlay, sprArrayPlay, matrixDataPlay);
			moveTo(0, 0);
			lineTo(Math.round(bgLarge/6), 0);
			lineTo(Math.round(bgLarge/6), Math.round(bgLarge/2));
			lineTo(0, Math.round(bgLarge/2));
			
			moveTo(Math.round(bgLarge/4), 0);
			lineTo(Math.round(bgLarge/4) + Math.round((bgLarge)/6), 0);
			lineTo(Math.round(bgLarge/4) + Math.round((bgLarge)/6), Math.round(bgLarge/2));
			lineTo(Math.round(bgLarge/4), Math.round(bgLarge/2));
			endFill();
		}
		mcPause._x = Math.round(mcControl._x + mcControl._width/2 - mcPause._width/2);
		mcPause._y = Math.round(mcControl._y + mcControl._height/2 - mcPause._height/2);
		
		
		//set status of the play and pause buttons
		if(Main.getInstance().mcAlbums.autoscrollBegin.toLowerCase() == "true")
		{
			isPlaying = true;
			mcPlay._visible = false;
			mcPlay._alpha = 0;
			mcPause._visible = true;
			mcPause._alpha = 100;
		}
		else
		{
			isPlaying = false;
			mcPause._visible = false;
			mcPause._alpha = 0;
			mcPlay._visible = true;
			mcPlay._alpha = 100;
		}
		
//		mcPlay.onRollOver = Proxy.create(this, controlsRollOver, mcPlay);
//		mcPlay.onRollOut = Proxy.create(this, controlsRollOut, mcPlay);
//		mcPlay.onRelease = Proxy.create(this, controlsRelease, mcPlay);
//		mcPause.onRollOver = Proxy.create(this, controlsRollOver, mcPause);
//		mcPause.onRollOut = Proxy.create(this, controlsRollOut, mcPause);
//		mcPause.onRelease = Proxy.create(this, controlsRelease, mcPause);
		
		mcControl.onRollOver = Proxy.create(this, controlsRollOver);
		mcControl.onRollOut = mcControl.onReleaseOutside = Proxy.create(this, controlsRollOut);
		mcControl.onRelease = Proxy.create(this, controlsRelease);
		
		mcScrollBtn.onPress = Proxy.create(this, dragging);
		mcScrollBtn.onRelease = mcScrollBtn.onReleaseOutside = Proxy.create(this, releasing);
		this.onEnterFrame = Proxy.create(this, scrolling);
		mcScrollBtn.onRollOver = Proxy.create(this, scrollBtnOver);
		mcScrollBtn.onRollOut = Proxy.create(this, scrollBtnOut);
		
		mcBg.onRollOver = Proxy.create(this, bgRollOver);
		mcBg.useHandCursor = false;
		mcScrollBg.onRelease = Proxy.create(this, scrollBgRelease);
		//mcScrollBg.useHandCursor = false;
	}
	
	private function scrollBgRelease() : Void
	{
		if(mcScrollBg._xmouse < mcScrollBtn._width/2)
		{
			_global['clearTimeout'](releaseBgTimeout);
			_global['clearTimeout'](autoscrollTimeout);
			if(mcPlay._visible != true)
			{
				autoScroll(true, Main.getInstance().mcAlbums.sWidth);
			}
			else
			{
				var percentX : Number = (border - mcScrollBg._x)/(mcScrollBg._width - mcScrollBtn._width);
				var gotoX : Number = Math.round(mcMask._x - percentX * (mcContent._width - mcMask._width));
				caurina.transitions.Tweener.addTween(mcContent, {_x:mcMask._x, time:2, transition:"easeOutExpo"});
			}
			caurina.transitions.Tweener.addTween(mcScrollBtn, {_x:border, time:0.5, transition:"easeOutExpo"});
		}
		else
		{
			if(mcScrollBg._xmouse > mcScrollBg._width - mcScrollBtn._width/2)
			{
				_global['clearTimeout'](releaseBgTimeout);
				_global['clearTimeout'](autoscrollTimeout);
				if(mcPlay._visible != true)
				{
					autoScroll(true, Main.getInstance().mcAlbums.sWidth);
				}
				else
				{
					var percentX : Number = (mcScrollBg._width - mcScrollBtn._width + border - mcScrollBg._x)/(mcScrollBg._width - mcScrollBtn._width);
					var gotoX : Number = Math.round(mcMask._x - percentX * (mcContent._width - mcMask._width));
					caurina.transitions.Tweener.addTween(mcContent, {_x:mcMask._x + mcMask._width - mcContent._width, time:2, transition:"easeOutExpo"});
				}
				caurina.transitions.Tweener.addTween(mcScrollBtn, {_x:mcScrollBg._width - mcScrollBtn._width + border, time:0.5, transition:"easeOutExpo"});
			} 
			else
			{
				_global['clearTimeout'](releaseBgTimeout);
				_global['clearTimeout'](autoscrollTimeout);
				if(mcPlay._visible != true)
				{
					autoScroll(true, Main.getInstance().mcAlbums.sWidth);
				}
				else
				{
					var percentX : Number = (mcScrollBg._xmouse - mcScrollBtn._width/2 - mcScrollBg._x)/(mcScrollBg._width - mcScrollBtn._width);
					var gotoX : Number = Math.round(mcMask._x - percentX * (mcContent._width - mcMask._width));
					caurina.transitions.Tweener.addTween(mcContent, {_x:gotoX, time:2, transition:"easeOutExpo"});
				}
				caurina.transitions.Tweener.addTween(mcScrollBtn, {_x:mcScrollBg._xmouse - mcScrollBtn._width/2, time:0.5, transition:"easeOutExpo"});
			}
		}
	}
	
	private function bgRollOver() : Void
	{
		
	}
	
	private function scrollBtnOver() : Void
	{
		caurina.transitions.Tweener.addTween(mcScrollBtn, {_alpha:80, time:0.5, transition:"easeOutExpo"});
	}
	private function scrollBtnOut() : Void
	{
		caurina.transitions.Tweener.addTween(mcScrollBtn, {_alpha:100, time:0.5, transition:"easeOutExpo"});
	}
	
	/**
	 * controls on roll over
	 */
	private function controlsRollOver() : Void
	{
		if(mcPlay._visible == true)
		{
			caurina.transitions.Tweener.addTween(mcPlay, {_alpha:50, time:0.5, transition:"easeOutExpo"});
		}
		if(mcPause._visible == true)
		{
			caurina.transitions.Tweener.addTween(mcPause, {_alpha:50, time:0.5, transition:"easeOutExpo"});
		}
	}
	
	/**
	 * controls on roll out
	 */
	private function controlsRollOut(mc : MovieClip) : Void
	{
		if(mcPlay._visible == true)
		{
			caurina.transitions.Tweener.addTween(mcPlay, {_alpha:100, time:0.5, transition:"easeOutExpo"});
		}
		if(mcPause._visible == true)
		{
			caurina.transitions.Tweener.addTween(mcPause, {_alpha:100, time:0.5, transition:"easeOutExpo"});
		}
	}
	
	/**
	 * controls release
	 */
	private function controlsRelease() : Void
	{
		if(mcPlay._visible == true)
		{
			isPlaying = true;
			Main.getInstance().mcAlbums.autoscrollBegin = "true";
			mcPlay._visible = false;
			mcPause._visible = true;
			mcPause._alpha = 100;
			autoScroll(true, Main.getInstance().mcAlbums.sWidth);
		}
		else
		{
			if(mcPause._visible == true)
			{
				_global['clearTimeout'](autoscrollTimeout);
				_global['clearTimeout'](releaseBgTimeout);
				isPlaying = false;
				Main.getInstance().mcAlbums.autoscrollBegin = "false";
				mcPause._visible = false;
				mcPlay._visible = true;
				mcPlay._alpha = 100;
				autoScroll(false, Main.getInstance().mcAlbums.sWidth);
			}
		}
	}
	
	/**
	 * autoscroll function
	 */
	public function autoScroll(bDirection : Boolean, maxPos : Number) : Void
	{
		mcContent.onEnterFrame = Proxy.create(this, autoscrolling);
		if(direction == true)
		{
			mcScrollBg._x = border;
			//mcScrollBtn._x = border;
			maxWidth = maxPos - pauseLength + 1;
		}
		else
		{
			mcScrollBg._y = border;
			//mcScrollBtn._y = border;
			maxHeight = maxPos;
		}
		if(bDirection == true)
		{
			autoscrolling();
		}
		else
		{
			delete mcContent.onEnterFrame;
		}
	}
	
	/**
	 * drag over the scroll bar button
	 */
	public function dragging() : Void
	{ 
		_global['clearTimeout'](releaseBgTimeout);
		_global['clearTimeout'](autoscrollTimeout);
		if(isPlaying == true)
		{
			Main.getInstance().mcAlbums.autoscrollBegin = "false";
			mcPause._visible = false;
			mcPlay._visible = true;
			mcPlay._alpha = 100;
			autoScroll(false, Main.getInstance().mcAlbums.sWidth);
		}
		if(direction == true)
		{
			mcScrollBtn.startDrag(false, mcScrollBg._x , mcScrollBg._y, mcScrollBg._x + mcScrollBg._width - mcScrollBtn._width + 1, mcScrollBg._y);
		}
		else
		{
			mcScrollBtn.startDrag(false, mcScrollBg._x , mcScrollBg._y, mcScrollBg._x, mcScrollBg._y + mcScrollBg._height - mcScrollBtn._height);
		}
		delete mcContent.onEnterFrame;
		this.onEnterFrame = Proxy.create(this, scrolling);
		
	}
	
	public function albumOverStopMove() : Void
	{
		if(isPlaying == true)
		{
			Main.getInstance().mcAlbums.autoscrollBegin = "false";
			mcPause._visible = false;
			mcPlay._visible = true;
			mcPlay._alpha = 100;
			autoScroll(false, Main.getInstance().mcAlbums.sWidth);
		}
		delete mcContent.onEnterFrame;
	}
	
	public function albumOutBeginMove() : Void
	{
		if(isPlaying == true)
		{
			Main.getInstance().mcAlbums.autoscrollBegin = "true";
			mcPlay._visible = false;
			mcPause._visible = true;
			mcPause._alpha = 100;
			autoScroll(true, Main.getInstance().mcAlbums.sWidth);
		}

		if(Main.getInstance().mcAlbums.autoscrollBegin.toLowerCase() == true)
		{
			mcContent.onEnterFrame = Proxy.create(this, autoscrolling);
		}
	}
	
	/**
	 * scroll bar button release
	 */
	private function releasing() : Void
	{
		if(isPlaying == true)
		{
			Main.getInstance().mcAlbums.autoscrollBegin = "true";
			mcPlay._visible = false;
			mcPause._visible = true;
			mcPause._alpha = 100;
			_global['clearTimeout'](releaseBgTimeout);
			releaseBgTimeout = _global['setTimeout'](this, 'autoScroll', 2000, true, Main.getInstance().mcAlbums.sWidth);
		}
		mcScrollBtn.stopDrag();
		if(Main.getInstance().mcAlbums.autoscrollBegin.toLowerCase() == true)
		{
			mcContent.onEnterFrame = Proxy.create(this, autoscrolling);
		}
	}
	
	/**
	 * scrolling function
	 */
	private function scrolling() : Void
	{
		if(direction == true)
		{
			var percentX : Number = (mcScrollBtn._x - mcScrollBg._x)/(mcScrollBg._width - mcScrollBtn._width);
			var gotoX : Number = Math.round(mcMask._x - percentX * (mcContent._width - mcMask._width));
			caurina.transitions.Tweener.addTween(mcContent, {_x:gotoX, time:2, transition:"easeOutExpo"});
		}
		else
		{
			var percentY : Number = (mcScrollBtn._y - mcScrollBg._y)/(mcScrollBg._height - mcScrollBtn._height);
			var gotoY : Number = Math.round(mcMask._y - percentY * (mcContent._height - mcMask._height));
			caurina.transitions.Tweener.addTween(mcContent, {_y:gotoY, time:2, transition:"easeOutExpo"});
		}	
	}
	
	/**
	 * autoscrolling function
	 */
	public function autoscrolling() : Void
	{
		
		if(direction == true)
		{
			if(mcScrollBtn._x < (maxWidth - mcScrollBtn._width - 2* border + 1))
			{
				if(changeDirection == false)
				{
						mcScrollBtn._x += Main.getInstance().mcAlbums.autoscrollingSpeed;
				}
				else
				{
					if(mcScrollBtn._x > border)
					{
							mcScrollBtn._x -= Main.getInstance().mcAlbums.autoscrollingSpeed;
					}
					else
					{
							changeDirection = false;
							mcScrollBtn._x += Main.getInstance().mcAlbums.autoscrollingSpeed;
							delete mcContent.onEnterFrame;
							_global['clearTimeout'](autoscrollTimeout);
							autoscrollTimeout = _global['setTimeout'](this, 'autoScroll', Main.getInstance().mcAlbums.autoslidePause * 1000, true, Main.getInstance().mcAlbums.sWidth);
					}
				}
			}
			else
			{
				changeDirection = true;
				mcScrollBtn._x -= Main.getInstance().mcAlbums.autoscrollingSpeed;
				delete mcContent.onEnterFrame;
				_global['clearTimeout'](autoscrollTimeout);
				autoscrollTimeout = _global['setTimeout'](this, 'autoScroll', Main.getInstance().mcAlbums.autoslidePause * 1000, true, Main.getInstance().mcAlbums.sWidth);
			}
			var percentX : Number = (mcScrollBtn._x - mcScrollBg._x)/(mcScrollBg._width - mcScrollBtn._width);
			var gotoX : Number = Math.round(mcMask._x - percentX * (mcContent._width - mcMask._width));
			mcContent._x = gotoX;
		}
		else
		{
			if(mcScrollBtn._y < (maxHeight - mcScrollBtn._height))
			{
				if(changeDirection == false)
				{
					mcScrollBtn._y += 1;
				}
				else
				{
					if(mcScrollBtn._y > 0)
					{
						mcScrollBtn._y -= 1;
					}
					else
					{
						changeDirection = false;
						mcScrollBtn._y += 1;
					}
				}
			}
			else
			{
				changeDirection = true;
				mcScrollBtn._y -= 1;
			}
			var percentY : Number = (mcScrollBtn._y - mcScrollBg._y)/(mcScrollBg._height - mcScrollBtn._height);
			var gotoY : Number = Math.round(mcMask._y - percentY * (mcContent._height - mcMask._height));
			mcContent._y = gotoY;
		}
	}
	
	public function resetScroll() : Void
	{
		mcScrollBtn._x = border;
	}
}
