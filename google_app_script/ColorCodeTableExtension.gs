function colorCodeTable() {  
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();  
  const range = sheet.getDataRange(); // Gets the range with data  
  const values = range.getValues();  
  
  const numRows = values.length;  
  const numCols = values[0].length;  
  
  // Prepare arrays for batch updates  
  const bgColors = new Array(numRows).fill().map(() => new Array(numCols).fill(null));  
  const fontColors = new Array(numRows).fill().map(() => new Array(numCols).fill(null));  
  
  // Initialize the color map  
  const colorMaps = new Array(numCols).fill().map(() => ({}));  
  
  // Generate color assignments  
  for (let col = 0; col < numCols; col++) { // Iterate over columns  
    const colorMap = colorMaps[col]; // Get the color map for this column  
    for (let row = 1; row < numRows; row++) { // Start from row 1 to skip header  
      const value = values[row][col];  
      if (!value) continue; // Skip blank cells  
  
      // Assign color if it's a new value in this column  
      if (!colorMap[value]) {  
        const bgColor = getRandomColor();  
        colorMap[value] = { bgColor: bgColor, textColor: getContrastingTextColor(bgColor) };  
      }  
  
      // Set the background and text color for the cell in the batch arrays  
      bgColors[row][col] = colorMap[value].bgColor;  
      fontColors[row][col] = colorMap[value].textColor;  
    }  
  }  
  
  // Apply background colors and font colors in a single batch update  
  range.setBackgrounds(bgColors);  
  range.setFontColors(fontColors);  
}  
  
function getRandomColor() {  
  return "#" + Math.random().toString(16).slice(2, 8);  
}  
 
function getContrastingTextColor(bgColor) {  
  const rgb = hexToRgb(bgColor);  
  // https://www.w3.org/WAI/GL/wiki/Relative_luminance  
  const luminance = (0.2126 * rgb.r + 0.7152 * rgb.g + 0.0722 * rgb.b) / 255;  
  // Return white text for dark backgrounds, black text for light backgrounds  
  return luminance > 0.5 ? '#000000' : '#FFFFFF';  
}  
  
function hexToRgb(hex) {  
  const bigint = parseInt(hex.slice(1), 16);  
  return {  
    r: (bigint >> 16) & 255,  
    g: (bigint >> 8) & 255,  
    b: bigint & 255  
  };  
}  

function onOpen() {  
  const ui = SpreadsheetApp.getUi();  
  ui.createMenu("Custom Tools")  
    .addItem("Color Code Table", "colorCodeTable") // Adds menu item  
    .addToUi();  
}