import RuleClass
import RuleComponent


OneRuleFile=RuleComponent.RuleFile()

OneFolder1=RuleComponent.RuleFolder()
OneFolder1_1=RuleComponent.RuleFolder()
OneFolder1_2=RuleComponent.RuleFolder()

OneFolder1_1.contains=["Rule A","Rule B"]
OneFolder1_2.contains=["Rule 1","Rule 2"]

OneFolder1.contains=[OneFolder1_1,OneFolder1_2]
OneRuleFile.contains=[OneFolder1]


OneRuleFile.run()
