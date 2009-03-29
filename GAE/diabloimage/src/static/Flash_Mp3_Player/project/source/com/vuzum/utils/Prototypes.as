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
 
import flash.geom.Matrix;
import flash.filters.BitmapFilter;
import flash.filters.ColorMatrixFilter;

class com.vuzum.utils.Prototypes
{
    public function Prototypes()
    {
    	/**
    	 * changes the color of a MovieClip
    	 * @param pColor the new color
    	 */
        MovieClip.prototype.setColor = function(pColor : Number):Void 
        {
            var mycol : Color = new Color(this);
            mycol.setRGB(pColor);
        };
        
        
        /**
         * Changes the brightness of a MovieClip
         *@param level the new level of Brightness
         *@return Void 
         */
        MovieClip.prototype.setBrightness = function(level : Number) : Void
        {
            var myElements_array:Array = 
                                       [1, 0, 0, 0, level,
                                        0, 1, 0, 0, level,
                                        0, 0, 1, 0, level,
                                        0, 0, 0, 1, 0];
            var myColorMatrix_filter:ColorMatrixFilter = new ColorMatrixFilter(myElements_array);
            this.filters = [myColorMatrix_filter];
        };
		
		
		/**
		 * Draws a shape polygon, with a desired color, in a MovieClip
		 * @param pArray an array of points
		 * @param pColor the color of shape
		 */
        MovieClip.prototype.drawPolygon = function (pArray : Array, pColor : Number) : Void
        {
            if (pColor == undefined)
            {
                pColor = 0xFEFEFE;
            }
            this.clear();
            this.beginFill(pColor);
            this.moveTo(pArray[0].x, pArray[0].y);
            for (var i : Number = 1;i < pArray.length; i++)
            {
                this.lineTo(pArray[i].x, pArray[i].y);
            }
            this.lineTo(pArray[0].x, pArray[0].y);
            this.endFill();
        };
        
        
        /**
         * Draws a gradient shape in a MovieClip
         * @param pWidth the width of the shape
         * @param pHeight the height of the shape
         * @param pType the type of gradient: linear or radial
         * @param pColors the colors for gradient
         * @param pAlphas the alphas for each color
         * @param pAngle the angle for gradient
         */
        MovieClip.prototype.applyGradientFill = function(pWidth : Number, pHeight : Number, pType : String, pColors : Array, pAlphas : Array, pAngle : Number) : Void
        {
            var myMatrix : Matrix = new Matrix();
            myMatrix.createGradientBox(pWidth, pHeight, pAngle * Math.PI / 180);
    	
            this.clear();
            this.beginGradientFill(pType, pColors, pAlphas, [0, 0xFF], myMatrix);
            this.moveTo(0, 0);
            this.lineTo(pWidth, 0);
            this.lineTo(pWidth, pHeight);
            this.lineTo(0, pHeight);
            this.lineTo(0, 0);
            this.endFill();
        };
        
        
        /**
         * Elastic effect with bounce for a MovieClip
         * @param centerx the new x position of MovieClip         * @param centery the new y position of MovieClip
         * @param inertia the speed of effect
         * @param k a constant used for bounce effect
         */
        MovieClip.prototype.move = function (centerx : Number,centery : Number,inertia : Number,k : Number):Void 
        {
            if (this.xp == undefined)
            {
                this.xp = 0;                this.yp = 0;
            }
        	
            var x : Number = -this._x + centerx ;
            var y : Number = -this._y + centery ;
	
            this.xp = this.xp * inertia + x * k ;
            this.yp = this.yp * inertia + y * k ;

            this._x += this.xp ;
            this._y += this.yp ;
        };
        
        
        /**
         * Elastic effect for a MovieClip
         * @param prop the elastic effect will be applied to these properties
         * @param speed the speed for elastic effect
         * @param f the callback function
         */
        MovieClip.prototype.elastic = function(prop : Array, speed : Number, f : Function):Void  
        {
            delete this.onEnterFrame;
            
            for (var i:String in prop) 
            {
                prop[i] = Math.round(prop[i]);                this[i] = Math.round(this[i]);
            }
            
            this.onEnterFrame = function():Void  
            {
                var propsNo : Number = 0;
                var propsFinished : Number = 0;
            	
                for (var i:String in prop) 
                {
                    propsNo++;
                    if (this[i] == prop[i]) 
                    {
                        propsFinished++;
                    }else
                    {
                        if (speed == 0 || Math.round((prop[i] - this[i]) / speed) == 0) 
                        {
                            this[i] = int(prop[i]);
                            propsFinished++;
                        }else
                        {
                            this[i] += Math.round((prop[i] - this[i]) / speed);
                        }
                    }
                }
                
                if (propsNo == propsFinished)
                {
                    delete this.onEnterFrame;
                    f();
                }
            };
        };
        
        
        
        /**
         * It adds successively 1, 2, 3 etc. (maxdot defined in function) at the end of string
         * @param mydottext the dot (char) will be added to this string
         * @param char to add at the end of string
         */
        MovieClip.prototype.dotrun = function(mydottext : String, char : String) : Void
        {
            this.dots = 0;
            this.dotdir = 0;
            if (char == undefined)
            {
                char = ".";
            }
            this.maxdot = 4;
            this.onEnterFrame = function() : Void
            {
                this.dots += this.dotdir;
                if (this.dots >= this.maxdot)
                {
                    this.dotdir = -1;
                }
				else if (this.dots < 1)
                {
                    this.dotdir = 1;
                }
                this.tempdots = "";
                for (var dc : Number = 0;dc < this.dots; dc++)
                {
                    this.tempdots += char;
                }
                this.txt.htmlText = mydottext + this.tempdots;
            };
        };
		
		
		/**
		 * TypeWriter effect
		 * @param newtext
		 * @param oldtext the original text
		 * @param lspeed the speed for writing the text
		 * @param blinkdelay the time interval for displaying "_"
		 * @param f calback function
		 * @param v parameter for callback function
		 */
        MovieClip.prototype.typewriter = function(newtext : String, oldtext : String, lspeed : Number, blinkdelay : Number, f : Function, v : Object) : Void 
        {
            this.charToUse = " ";
            //
            if (oldtext == null)
            {
                oldtext = "";
            }
            this.temptext = oldtext;
            this.counter = 0;
            this.i = oldtext.length;
            if (lspeed == null)
            {
                lspeed = 1;
            }
            if (blinkdelay == null)
            {
                blinkdelay = 31;
            }
			
            this.onEnterFrame = function() : Void 
            {
                for (var mylspeed : Number = 0;mylspeed < lspeed; mylspeed++)
                {
                    this.temptext = this.temptext + newtext.charAt(this.i);
                    if (newtext.charAt(this.i) == "<")
                    {
                        var htmlend : Number = newtext.indexOf(">", this.i);
                        var htmladd : Number = htmlend - this.i;
                        this.i = this.i + htmladd;
                        this.temptext = newtext.substr(0, this.i);
                        continue;
                    }
                    this.i++;
                }
                this.txt.htmlText = this.temptext + this.charToUse;
                if (this.i >= newtext.length)
                {
                    this.mybool = 1;
                    this.onEnterFrame = function():Void 
                    {
                        this.counter++;
                        this.mybool = !this.mybool;
                        if (this.mybool == true)
                        {
                            this.txt.htmlText = this.temptext + this.charToUse;
                        }
						else
                        {
                            this.txt.htmlText = this.temptext;
                        }
                        if (this.counter >= blinkdelay)
                        {
                            this.txt.htmlText = this.temptext;
                            this.counter = 0;
                            this.blinkremove();
                            delete this["onEnterFrame"];
                            f(v);
                        }
                    };
                }
            };
        };
        
        
        /**
         * It removing the movieclip used for blink TypeWriter effect
         */
        MovieClip.prototype.blinkremove = function():Void 
        {
            this.onEnterFrame = function():Void 
            {
                this._alpha = this._alpha - 10;
                this._visible = !this._visible;
                if (this._alpha <= 0)
                {
                    this.removeMovieClip();
                }
            };
        };
        
        
        /**
         * Disable a MovieClip
         */
        MovieClip.prototype.disable = function():Void 
        {
            this._alpha = 50;
            this.enabled = false;
            this.useHandCursor = false;
        };
        
        
        /**
         * Enable a MovieClip
         */
        MovieClip.prototype.enable = function():Void 
        {
            this._alpha = 100;
            this.enabled = true;
            this.useHandCursor = true;
        };
        
        
        /**
         * Calculates the _root position for a MovieClip
         * @return _root position for MovieClip
         */
        MovieClip.prototype.getRootXY = function():Object
        {
            var xyPos : Object = new Object();
            xyPos.x = xyPos.y = 0;
            var myMovieClip : Object = this;
		
            while (myMovieClip != _root)
            {
                xyPos.x += myMovieClip._x;
                xyPos.y += myMovieClip._y;
                myMovieClip = myMovieClip._parent;
            }
		
            return xyPos;
        };
        
        
        /**
         * Converts a MovieClip colors to Garyscale
         */
		MovieClip.prototype.setToGrayscale = function() : Void
		
		{
		
			this.cacheAsBitmap = true;
		
			var matrix:Array = new Array();
		
			matrix = matrix.concat([0.308600038290024, 0.609399974346161, 0.0820000022649765, 0, 0]);
		
			// red
		
			matrix = matrix.concat([0.308600008487701, 0.609399974346161, 0.0820000022649765, 0, 0]);
		
			//green
		
			matrix = matrix.concat([0.308600008487701, 0.609399974346161, 0.0820000246167183, 0, 0]);
		
			// blue
		
			matrix = matrix.concat([0, 0, 0, 1, 0]);
		
			// alpha
		
			var filter:BitmapFilter = new ColorMatrixFilter(matrix);
		
			this.filters = new Array(filter);
		
		};
		
		
		/**
		 * Removes Grayscale form a MovieClip
		 */
		MovieClip.prototype.removeGrayscale = function() : Void
		{
			this.filters = new Array();
		};

        
        //************************************************************//
        //  					STRING
        //************************************************************//


		/**
		* Replaces a substring in a string
		* @param replaceFrom what to replece
		* @param replaceTo to what to raplace
		* @param caseSensitive true or false
		* @return replaced string
		*/
        String.prototype.replaceSubString = function (replaceFrom : String, replaceTo : String, caseSensitive : Boolean) : String 
        {
            var start : Array = this.split(replaceFrom);
            var tmp : String = start.join(replaceTo);
            if (!caseSensitive) 
            {
                start = tmp.split(replaceFrom.toLowerCase());
                tmp = start.join(replaceTo);
                start = tmp.split(replaceFrom.toUpperCase());
                tmp = start.join(replaceTo);
            }
            return tmp;
        };
		
		
		/**
		 * Validates if a String is a valid email address or not
		 * @return true if is a valid email address, false if is not a valid email address
		 */
        String.prototype.isEmail = function() : Boolean
        {
            // email address has to have at least 5 chars
            if (this.length < 6)
            {
                return false;
            }
			
			// not allowed charcters
            var iChars : String = "*|,\":<>[]{}`';()&$#%+=";
            var eLength : Number = this.length;
            for (var i : Number = 0;i < eLength; i++)
            {
                if (iChars.indexOf(this.charAt(i)) != -1)
                {
                    //trace("Invalid Email Address : Illegal Character in Email Address : -->"+this.charAt(i)+"<--.");
                    return false;
                }
            }
			
			// position of @
            var atIndex : Number = this.lastIndexOf("@");
            if (atIndex < 1 || (atIndex == eLength - 1))
            {
                //trace("Invalid Email Address : Email Address must contain @ as at least the second chararcter.");
                return false;
            }
            // 2 of @ are not allowed
            if(this.indexOf("@") != atIndex) return false;
            
            // position of last .
            var dotIndex : Number = this.lastIndexOf(".");
            if (dotIndex < 4 || (dotIndex == eLength - 1) || (dotIndex >= eLength-2))
            {
                //trace("Invalid Email Address : Email Address must contain at least one . (period) in a valid position");
                return false;
            }
            
            // position of last . after @
            if (1 >= dotIndex - atIndex)
            {
                //trace("Invalid Email Address : Email Address must be in the form of name@domain.domaintype");
                return false;
            }
            
            
            // not 2 of . or @ consequently
            for (i = 0; i < eLength; i++)
            {
                if ((this.charAt(i) == "." || this.charAt(i) == "@") && this.charAt(i) == this.charAt(i - 1))
                {
                    //trace("Invalid Email Address : Cannot contain two \".\" or \"@\" in a row : -->" + this.charAt(i) + "<--.");
                    return false;
                }
            }
            
            return true;
        };
    }
}
