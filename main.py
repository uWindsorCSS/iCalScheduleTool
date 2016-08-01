from uwindsorclient import UWindsorClient

c = UWindsorClient()
c.PromptLogin()
c.GenerateICalFile()
