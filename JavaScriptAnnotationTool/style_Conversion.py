import os
import re
import xml.etree.ElementTree as ET
from lxml import etree
from io import BytesIO
import codecs

class CleanDownloadedAct:
    
    @staticmethod
    def main(args):
        if len(args) == 2:
            CleanDownloadedAct.process_file(args[0], args[1])
        else:
            # Fallback to default file paths if arguments are not provided.
            folder = os.path.join("sample")
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    if file.lower().endswith(".xhtml"):
                        input_file_path = os.path.join(folder, file)
                        output_file_path = os.path.join("./output_folder/", file)
                        CleanDownloadedAct.process_file(input_file_path, output_file_path)
            else:
                print("The folder is empty or does not exist.")
    
    @staticmethod
    def process_folder(input_folder,output_folder):
        folder = os.path.join(input_folder)
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.lower().endswith(".xhtml"):
                    input_file_path = os.path.join(folder, file)
                    output_file_path = os.path.join(output_folder, file)
                    CleanDownloadedAct.process_file(input_file_path, output_file_path)
        else:
            print("The folder is empty or does not exist.")
    @staticmethod
    def update_style_paths(head):
        if head is not None:
            for style in head.findall("{http://www.w3.org/1999/xhtml}style"):
                if style.text:
                    style.text = style.text.replace('@import "styles/', '@import "../styles/')
    @staticmethod
    def process_file(input_file_path, output_file_path):
        try:
            # Create File objects using the provided paths
            input_file = input_file_path
            output_file = output_file_path

            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            text = CleanDownloadedAct.remove_undesired_text(text)
            
            # Parse the XML
            parser = etree.XMLParser(remove_blank_text=True)
            doc = etree.parse(BytesIO(text.encode('utf-8')), parser)
            root = doc.getroot()
            
            # Add namespace declaration
            nsmap = root.nsmap
            if nsmap is None:
                nsmap = {}
            nsmap['xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
            
            # Find the head element
            head = root.find("{http://www.w3.org/1999/xhtml}head")
            #print(head)
            if head is not None:
                CleanDownloadedAct.update_style_paths(head)
                # Create script content
                script_content = "//<![CDATA[\n" \
                    "window.addEventListener(\"message\", function(event) {\n" \
                    "    if (event.data.type === \"highlight\") {\n" \
                    "        // Remove any previous highlights\n" \
                    "        removePreviousHighlights();\n" \
                    "\n" \
                    "        // Obtain and normalize the search text.\n" \
                    "        let searchText = normalizeText(event.data.text);\n" \
                    "        console.log(\"Received text to highlight:\", searchText);\n" \
                    "\n" \
                    "        let section = event.data.section;\n" \
                    "        console.log(\"Received text to highlight in section:\", section);\n" \
                    "\n" \
                    "        // Normalize the document to merge adjacent text nodes.\n" \
                    "        document.body.normalize();\n" \
                    "\n" \
                    "        // Determine the section boundaries.\n" \
                    "        // We assume that the section is marked by an anchor with id \"section-\" + section.\n" \
                    "        let sectionId = \"section-\" + section;\n" \
                    "        let startAnchor = document.getElementById(sectionId);\n" \
                    "        if (!startAnchor) {\n" \
                    "            console.warn(\"No start anchor found for section:\", sectionId);\n" \
                    "            return;\n" \
                    "        }\n" \
                    "\n" \
                    "        // Find the next section anchor, if any, to mark the boundary end.\n" \
                    "        let anchors = Array.from(document.querySelectorAll(\"a.LegAnchorID\"));\n" \
                    "        let boundaryAnchor = null;\n" \
                    "        for (let i = 0; i < anchors.length; i++) {\n" \
                    "            if (anchors[i] === startAnchor && i < anchors.length - 1) {\n" \
                    "                boundaryAnchor = anchors[i + 1];\n" \
                    "                break;\n" \
                    "            }\n" \
                    "        }\n" \
                    "\n" \
                    "        // Helper function to check if a text node is between the start and boundary anchors.\n" \
                    "        function isNodeInSection(node, start, boundary) {\n" \
                    "            let afterStart = start.contains(node) || !!(start.compareDocumentPosition(node) & Node.DOCUMENT_POSITION_FOLLOWING);\n" \
                    "            let beforeBoundary = true;\n" \
                    "            if (boundary) {\n" \
                    "                beforeBoundary = !!(boundary.compareDocumentPosition(node) & Node.DOCUMENT_POSITION_PRECEDING);\n" \
                    "            }\n" \
                    "            return afterStart && beforeBoundary;\n" \
                    "        }\n" \
                    "\n" \
                    "        // Create a TreeWalker to iterate through all text nodes.\n" \
                    "        let walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);\n" \
                    "        let node;\n" \
                    "        let found = false;\n" \
                    "\n" \
                    "        while ((node = walker.nextNode())) {\n" \
                    "            if (!isNodeInSection(node, startAnchor, boundaryAnchor)) continue;\n" \
                    "\n" \
                    "            let normalizedNodeText = normalizeText(node.nodeValue);\n" \
                    "            let index = normalizedNodeText.toLowerCase().indexOf(searchText.toLowerCase());\n" \
                    "            if (index !== -1) {\n" \
                    "                console.log(\"Match found in node:\", node.nodeValue);\n" \
                    "                let range = document.createRange();\n" \
                    "                try {\n" \
                    "                    range.setStart(node, index);\n" \
                    "                    range.setEnd(node, index + searchText.length);\n" \
                    "                } catch (error) {\n" \
                    "                    console.error(\"Error setting range:\", error);\n" \
                    "                    break;\n" \
                    "                }\n" \
                    "                let span = document.createElement(\"span\");\n" \
                    "                span.className = \"highlight\";\n" \
                    "                span.style.backgroundColor = \"yellow\";\n" \
                    "                span.style.color = \"black\";\n" \
                    "                span.style.fontWeight = \"bold\";\n" \
                    "                try {\n" \
                    "                    range.surroundContents(span);\n" \
                    "                    console.log(span);\n" \
                    "                    console.log(range);\n" \
                    "                } catch (error) {\n" \
                    "                    console.error(\"Error surrounding contents:\", error);\n" \
                    "                }\n" \
                    "                found = true;\n" \
                    "                break;\n" \
                    "            }\n" \
                    "        }\n" \
                    "        if (!found) {\n" \
                    "            console.warn(\"No matching text found for:\", searchText);\n" \
                    "        }\n" \
                    "    }\n" \
                    "});\n" \
                    "//]]>" \
                    "// Function to remove any existing highlights\n" \
                    "function removePreviousHighlights() {\n" \
                    "let highlightedElements = document.querySelectorAll(\"span.highlight\");\n" \
                    "highlightedElements.forEach(span => {\n" \
                    "let parent = span.parentNode;\n" \
                    "// Replace the span with its text content\n" \
                    "let textNode = document.createTextNode(span.textContent);\n" \
                    "parent.replaceChild(textNode, span);\n" \
                    "});\n" \
                    "}\n" \
                    "// Function to normalize text for comparison\n" \
                    "function normalizeText(text) {\n" \
                    "return text.replace(/[\\u2018\\u2019]/g, \"'\");\n" \
                    "}\n"

                # Create script element
                script = etree.SubElement(head, "script")
                script.set("type", "text/javascript")
                script.text = script_content
            
            # Process the document
            CleanDownloadedAct.remove_undesired_elements(root)
            CleanDownloadedAct.remove_span_including_only_text_must_be_removed(root)
            CleanDownloadedAct.remove_double_removed_text_elements(root)
            # Do it twice because the merging might create a span with a single Text
            CleanDownloadedAct.remove_span_including_only_text_must_be_removed(root)
            CleanDownloadedAct.remove_double_removed_text_elements(root)
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Remove output file if it exists
            if os.path.exists(output_file):
                os.remove(output_file)
                
            # Write the output
            with open(output_file, 'wb') as f:
                f.write(etree.tostring(doc, pretty_print=True, encoding='UTF-8', xml_declaration=True))
                
        except Exception as e:
            print(f"{type(e).__name__}: {str(e)}")
    
    @staticmethod
    def remove_undesired_text(text):
        DOCTYPE = "\"http://www.w3.org/MarkUp/DTD/xhtml-rdfa-1.dtd\">"
        if DOCTYPE in text:
            text = text[text.index(DOCTYPE) + len(DOCTYPE):]
        
        while "/styles/" in text:
            text = text[:text.index("/styles/")] + \
                "styles/" + \
                text[text.index("/styles/") + len("/styles/"):]
        
        return text
    
    @staticmethod
    def remove_undesired_elements(e):
        remove = False
        remove_subsequents = False
        
        # Remove the "[" and the "]"
        if (e.tag.split("}")[-1].lower() == "span" and 
            e.get("class") is not None and 
            e.get("class").lower() == "legchangedelimiter"):
            remove = True
            
        # Remove the "F*" after the "["
        if (e.tag.split("}")[-1] == "a" and 
            e.get("class") is not None and 
            e.get("class").lower() == "legcommentarylink"):
            remove = True
            
        # Remove the table with passive modifications
        if (e.tag.split("}")[-1] == "div" and 
            e.get("class") is not None and 
            e.get("class").lower() == "legannotations"):
            remove = True
            
        # Remove all schedules
        if (e.tag.split("}")[-1] == "h1" and 
            e.get("class") is not None and 
            e.get("class").lower() == "legschedulestitle"):
            remove = True
            remove_subsequents = True
        
        # Check for amendments to other acts
        replace_text = CleanDownloadedAct.remove_other_acts_amendments(e)
        
        if remove:
            parent = e.getparent()
            if parent is None:
                return
                
            index = parent.index(e)
            parent.remove(e)
            
            # Remove subsequent elements if needed
            if remove_subsequents:
                for child in list(parent)[index:]:
                    parent.remove(child)
        
        elif replace_text is not None:
            # Clear the element and add the replacement text
            for child in list(e):
                e.remove(child)
            e.text = replace_text
            e.set("style", "color:red;font-weight:bold")
        
        else:
            # Process child elements
            for child in list(e):
                CleanDownloadedAct.remove_undesired_elements(child)
    
    @staticmethod
    def remove_other_acts_amendments(e):
        class_attribute = e.get("class")
        if class_attribute is None:
            return None
            
        amendment_classes = [
            "LegClearFix LegP2Container LegAmend",
            "LegClearFix LegP3Container LegAmend",
            "LegClearFix LegP4Container LegAmend",
            "LegRHS LegP1TextC1Amend",
            "LegRHS LegP2TextC1Amend",
            "LegRHS LegP3TextC1Amend",
            "LegTabbedDefC1Amend LegUnorderedListC1Amend",
            "LegPartNo LegC1Amend",
            "LegSP1GroupTitleFirstC1Amend",
            "LegClearFix LegSP1Container LegAmend",
            "LegClearFix LegSP2Container LegAmend",
            "LegClearFix LegSP3Container LegAmend",
            "LegSP1GroupTitleC1Amend",
            "LegPartTitle LegC1Amend",
            "LegTabbedDefC3Amend LegUnorderedListC3Amend",
            "LegDS LegP1NoC3Amend",
            "LegDS LegRHS LegP1TextC3Amend",
            "LegSP1GroupTitleFirstC3Amend",
            "LegChapterNo LegC1Amend",
            "LegChapterTitle LegC1Amend",
            "LegRHS LegP2TextC3Amend",
            "LegClearFix LegSP4Container LegAmend",
            "LegTextC1Amend",
            "LegDS LegP1GroupTitleFirstC1Amend",
            "LegDS LegP1NoC1Amend"
        ]
        
        if class_attribute.lower() not in [c.lower() for c in amendment_classes]:
            return None
            
        # Return replacement text
        #return "TEXT REMOVED. MUST NOT BE ANNOTATED"
        return " "
    
    @staticmethod
    def remove_span_including_only_text_must_be_removed(e):
        if (e.tag.split("}")[-1] != "span" or 
            len(e) > 0 or 
            e.text is None):
            for child in list(e):
                CleanDownloadedAct.remove_span_including_only_text_must_be_removed(child)
            return
        
        '''
        if e.text.strip() == "TEXT REMOVED. MUST NOT BE ANNOTATED":
            parent = e.getparent()
            if parent is None:
                return
            # Check if parent has no other elements or text besides this span
            if len(parent) == 1 and parent.text is None and parent[0].tail is None:
                parent.text = "" #"TEXT REMOVED. MUST NOT BE ANNOTATED"
                #parent.set("style", "color:red;font-weight:bold")
                parent.remove(e)
        '''
    
   
    @staticmethod
    def remove_double_removed_text_elements(e):
        if e.get("style") == "color:red;font-weight:bold":
            parent = e.getparent()
            if parent is None:
                return  # Element already removed in a previous recursion
            
            index = parent.index(e)
            
            if index > 0:
                prev_sibling = parent[index - 1]
                # If the previous element is also red, remove this one
                if prev_sibling.get("style") == "color:red;font-weight:bold":
                    parent.remove(e)
                # Otherwise, if this element has a class attribute, remove it
                elif e.get("class") is not None:
                    del e.attrib["class"]
        else:
            # Process child elements
            for child in list(e):
                CleanDownloadedAct.remove_double_removed_text_elements(child)

if __name__ == "__main__":
    import sys
    CleanDownloadedAct.process_folder("downloaded_acts","output_folder")