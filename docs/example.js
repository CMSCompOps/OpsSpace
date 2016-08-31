/*"""
.. describe:: example.js

Contains an example fuction for you to change div contents.

:author: Daniel Abercrombie <dabercro@mit.edu>
*/

function example (divId, content) {
    /*"""
    .. function:: example(divId, content)

       Changes the content of a given ``<div>``

       :param str divId: is the id of the ``<div>`` to change.
       :param str content: is the content to change the innerHTML to.
    */

    var theDiv = document.getElementById(divId);
    theDiv.innerHTML = content;

}
