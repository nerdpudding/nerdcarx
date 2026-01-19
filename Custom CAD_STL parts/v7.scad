// Raspberry Pi Camera Module 3 + OLED Mount - Versie 21 (Wider OLED Window)
// Save this text as "camera_mount_v21.scad"

$fn = 60;

// Variabelen
plaat_dikte = 3;
breedte = 34; 

camera_plaat_h = 30;
oled_plaat_h = 30; 
totaal_h = camera_plaat_h + oled_plaat_h;
totale_arm_diepte = 40; 
totale_gat_afstand = 27;

union() {
    // 1. DE HOOFDPLAAT
    difference() {
        cube([breedte, totaal_h, plaat_dikte]);

        // CAMERA
        translate([breedte/2 - 6, 15 - 6, -1]) cube([12, 12, 10]);
        translate([breedte/2 - 10.5, 15, -1]) cylinder(h=10, d=2.8);
        translate([breedte/2 + 10.5, 15, -1]) cylinder(h=10, d=2.8);
        translate([breedte/2 - 10.5, 27.5, -1]) cylinder(h=10, d=2.8);
        translate([breedte/2 + 10.5, 27.5, -1]) cylinder(h=10, d=2.8);

        // OLED GATEN
        // Horizontaal: 20mm.
        // Verticaal: 24mm.
        
        translate([7, 44 - 12, -1]) cylinder(h=10, d=2.8); // Onder (Y=32)
        translate([27, 44 - 12, -1]) cylinder(h=10, d=2.8);
        
        translate([7, 44 + 12, -1]) cylinder(h=10, d=2.8); // Boven (Y=56)
        translate([27, 44 + 12, -1]) cylinder(h=10, d=2.8);
        
        // HET WINDOW (AANGEPAST: 27.7 x 19.3)
        // Was 26.7, nu 27.7 (1mm breder totaal, 0.5mm per kant)
        translate([breedte/2 - (27.7/2), 44 - (19.3/2), -1])
            cube([27.7, 19.3, 10]);
            
        // KABEL RELIEF CUT
        translate([breedte/2 - 6, 32.35, -1]) cube([12, 4, 10]);
            
        // INKEPING BOVEN
        translate([breedte/2 - 6, totaal_h - 5, -1]) cube([12, 6, 10]);
    }

    // 2. ZIJ-ARM
    translate([0, 0, 0])
        rotate([0, -90, 0])
            translate([0, 0, -3])
            difference() {
                cube([totale_arm_diepte, 30, 3]);
                translate([totale_gat_afstand, 15, -1])
                    cylinder(h=10, d=8);
            }
}
