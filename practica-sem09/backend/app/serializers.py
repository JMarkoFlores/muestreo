def user_out(user):
    return {'id':user.id,'username':user.username,'email':user.email,'full_name':user.full_name,'roles':[r.name for r in user.roles]}

def triage_out(t):
    return None if not t else {'severity':t.severity,'verdict':t.verdict,'summary':t.summary,'recommendations':t.recommendations,'confidence':t.confidence,'provider':t.provider,'model':t.model,'error_message':t.error_message}

def alert_out(a):
    return {'id':a.id,'external_id':a.external_id,'source':a.source,'title':a.title,'description':a.description,'source_ip':a.source_ip,'destination_ip':a.destination_ip,'severity':a.severity,'status':a.status,'received_at':a.received_at,'completed_at':a.completed_at,'error_message':a.error_message,'triage':triage_out(a.triage),'enrichment':a.enrichment.data if a.enrichment else None}
