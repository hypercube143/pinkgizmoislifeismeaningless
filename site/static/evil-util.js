// some evil functions with some super evil uses
// evil util sounds like a names for a set of evil twins

function evilThousandsFormatter(x) { // format thousands 1000 -> 1,000 etc
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","); // very very evil regex
}