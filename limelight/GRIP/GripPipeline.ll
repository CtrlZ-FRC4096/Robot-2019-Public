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
    List hslThresholdHue = [30.755395683453237, 84.54545454545455];
    List hslThresholdSaturation = [199.50539568345323, 255.0];
    List hslThresholdLuminance = [20.638489208633093, 113.33333333333333];

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
    Double filterContoursMinArea = 100.0;
    Double filterContoursMinPerimeter = 0.0;
    Double filterContoursMinWidth = 30.0;
    Double filterContoursMaxWidth = 1000.0;
    Double filterContoursMinHeight = 0.0;
    Double filterContoursMaxHeight = 1000.0;
    List filterContoursSolidity = [0.0, 100.0];
    Double filterContoursMaxVertices = 1000000.0;
    Double filterContoursMinVertices = 0.0;
    Double filterContoursMinRatio = 0.0;
    Double filterContoursMaxRatio = 1000.0;

    filterContours(filterContoursContours, filterContoursMinArea, filterContoursMinPerimeter, filterContoursMinWidth, filterContoursMaxWidth, filterContoursMinHeight, filterContoursMaxHeight, filterContoursSolidity, filterContoursMaxVertices, filterContoursMinVertices, filterContoursMinRatio, filterContoursMaxRatio, filterContoursOutput);
}




