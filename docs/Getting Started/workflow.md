# General Workflow


EML files come in from multiple [Sources](/docs/Sources/README.md).

For each EML file, an initial extraction is performed
    1. Parse out the email
        - are there attachments to extract?
        - segment out header, body, and attachments
        - get statistcs about email (size, number of attachments, message type, etc)

    2. Prepare EML Vault Workspace
        - Copy file to Vault

    2. Extract Attachments 
        - is this email worth expanding for a full report?
        - 

    3. Header Analysis
        - extract all ip addresses, emails, domain names
        - expand on ip 
        - YARA Processor
            - Associate broken rules with EML
    
    4. Body Analysis

    5. Attachment Analysis
        - associate attachment with EML
        - filetype Detection
        - hash checking against [Virustotal](https://virustotal.com)
        - YARA Processor
            - Associate broken rules with Attachment
         
        - Sandboxing

After the initial check, the scan is sent to multiple [Services](../Services/README.md) for data enrichment:
    - do we want to keep the file?
