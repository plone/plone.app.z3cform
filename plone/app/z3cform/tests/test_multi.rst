*** Settings ***
Documentation   ...
Resource  plone/app/robotframework/selenium.robot
Test Setup  Open test browser
Test Teardown  Close all browsers

*** Variables ***


*** Test Cases ***

Test a multi form
    Go to   ${PLONE_URL}/@@test-multi-form
    Page should contain   Please enter the names and ages for each person
    Click Button  Add
    With the label  name 1  Input Text  Jane of the Jungle
    With the label  age 1  Input Text  25
    Click Button  Add
    With the label  name 2  Input Text  Jane of the Jungle
    With the label  age 2   Input Text  25
    Click Button  Apply

*** Keywords ***

With the label
    [arguments]     ${title}   ${extra_keyword}   @{list}
    ${for}=  Get Element Attribute  xpath=//label[starts-with(translate(normalize-space(.)," &#9;&#10;&#13", "-"), translate(normalize-space("${title}")," &#9;&#10;&#13", "-"))]@for
  #   ${for}  Execute Javascript   return $('label').filter(function(){return $(this).text().replace(/\s+/g,' ').trim()=='${title}'}).attr('for')[0]

    Run Keyword     ${extra_keyword}  id=${for}   @{list}



