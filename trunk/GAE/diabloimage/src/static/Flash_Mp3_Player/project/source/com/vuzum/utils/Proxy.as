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
 
class com.vuzum.utils.Proxy 
{
    public static function create(oTarget : Object, fFunction : Function) : Function 
    {

        var aParameters : Array = new Array();
        for(var i : Number = 2; i < arguments.length; i++) 
        {
            aParameters[i - 2] = arguments[i];
        }

        var fProxy : Function = function():Void 
        {
            var aActualParameters : Array = arguments.concat(aParameters);
            fFunction.apply(oTarget, aActualParameters);
        };

        return fProxy;
    }
}