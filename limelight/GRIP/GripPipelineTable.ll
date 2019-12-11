//
// Inputs
//
Inputs
{
	Mat source0;
	Mat source1;
}

//
// Variables
//
Outputs
{
	Mat maskOutput;
	Mat hslThresholdOutput;
	ContoursReport findContoursOutput;
	ContoursReport filterContoursOutput;
}

//
// Steps
//

Step Mask0
{
    Mat maskInput = source0;
    Mat maskMask = source1;

    mask(maskInput, maskMask, maskOutput);
}

Step HSL_Threshold0
{
    Mat hslThresholdInput = maskOutput;
    List hslThresholdHue = [27.51798561151079, 122.42424242424238];
    List hslThresholdSaturation = [0.0, 255.0];
    List hslThresholdLuminance = [137.58992805755395, 255.0];

    hslThreshold(hslThresholdInput, hslThresholdHue, hslThresholdSaturation, hslThresholdLuminance, hslThresholdOutput);
}

Step Find_Contours0
{
    Mat findContoursInput = hslThresholdOutput;
    Boolean findContoursExternalOnly = false;

    findContours(findContoursInput, findContoursExternalOnly, findContoursOutput);
}

Step Filter_Contours0
{
    ContoursReport filterContoursContours = findContoursOutput;
    Double filterContoursMinArea = 300.0;
    Double filterContoursMinPerimeter = 0;
    Double filterContoursMinWidth = 40.0;
    Double filterContoursMaxWidth = 1000.0;
    Double filterContoursMinHeight = 0;
    Double filterContoursMaxHeight = 1000;
    List filterContoursSolidity = [0.0, 100.0];
    Double filterContoursMaxVertices = 1000000;
    Double filterContoursMinVertices = 0;
    Double filterContoursMinRatio = 0;
    Double filterContoursMaxRatio = 1000;

    filterContours(filterContoursContours, filterContoursMinArea, filterContoursMinPerimeter, filterContoursMinWidth, filterContoursMaxWidth, filterContoursMinHeight, filterContoursMaxHeight, filterContoursSolidity, filterContoursMaxVertices, filterContoursMinVertices, filterContoursMinRatio, filterContoursMaxRatio, filterContoursOutput);
}




