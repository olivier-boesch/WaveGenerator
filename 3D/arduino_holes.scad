/*

Arduino holes

Olivier Boesch © 2021


*/

arduino_uno_holes = [
                        [14, 2.5],
                        [14+1.3+50.8, 2.5+5.1],
                        [14+1.3+50.8, 2.5+5.1+27.9],
                        [14+1.3, 2.5+5.1+27.9+15.2]
                    ];
                    
module arduino_uno_place_on_holes(){
    for(h=arduino_uno_holes){
        translate(h) children(0);
    }
}

arduino_uno_place_on_holes() cylinder(h=10, d=3.2, center=true);