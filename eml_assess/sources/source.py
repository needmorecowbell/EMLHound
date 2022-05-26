class Source():
    """Source
    
    Base EML File Source Class
    """
    
    def __init__(self,name="Unnamed Source"):
        self.name = name
        self.period_types = ["cron","dynamic","seconds"]
        self.cronschedule = "* * * * *"

    def check(self):
        """
            Sources should check each new EML and vet them before including them for reports
        """
        pass