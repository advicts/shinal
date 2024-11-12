from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
from dateutil import relativedelta
import pytz



class PartnerVisitController(http.Controller):

  @http.route('/api/visits', methods=['POST'], type="json", auth="public", website=True, csrf=False)
  def get_partner_visits(self, **kw):
    request_body = request.jsonrequest
    if not request.httprequest.headers.get('authorization'):
      #  TODO Remove Static Authorization Token and add it INTO .env OR Remove Token And Check by Request IP..
      return {
          "status": 403,
          "message": "Authentication Errors : Set Authorization Code in Header",
          "data": False
      }
    if request.httprequest.headers[
        'authorization'] != 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAvYXBpL2NsaWVudC9jYXJ0IiwiaWF0IjoxNjIyMzk2NjIxLCJleHAiOjE2MjI1Njk0MjIsIm5iZiI6MTYyMjM5NjYyMiwianRpIjoiRDJJcWxMdWp0YTBqS214UiIsInN1YiI6MywicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyIsIjAiOiJuYW1lIiwiMSI6ImVtYWlsIn0.LQzhPwfNRCiJkVNyN3qJMRNsQAKvvobSfFRPkZmL0Zw':
      return {"status": 403, "message": "Authentication Errors : not authenticate", "data": False}
    result = self._get_visits_json(request_body['user_id'])
    return result

  def _get_visits_json(self, user_id):
    visits = request.env['visits.visit'].sudo().search([('salesperson_id', '=', user_id),
                                                        ('visiting_date', '=', datetime.now()),
                                                        ('state', 'in', ['confirmed','done','inprogress'])])
    visits_lst = []
    utc_timezone = pytz.utc
    iraq_timezone = pytz.timezone('Asia/Baghdad')
    for visit in visits:
      visits_lst.append({
          'user_id': visit.salesperson_id.id,
          'visit_id': visit.id,
          'partner_id': visit.partner_id.id,
          'code': visit.name,
          'plannign': visit.visit_planning_id.name,
          'visiting_date':str(visit.visiting_date),
          'start_date': utc_timezone.localize(visit.start_date).astimezone(iraq_timezone).strftime('%Y-%m-%d %H:%M:%S') if visit.start_date else '',
          'state':visit.state
      })

    return visits_lst

  @http.route('/api/action/update_visit',
              methods=['POST'],
              type="json",
              auth="public",
              website=True,
              csrf=False)
  def action_update_visit(self, **kw):
      request_body = request.jsonrequest
      if not request.httprequest.headers.get('authorization'):
          #  TODO Remove Static Authorization Token and add it INTO .env OR Remove Token And Check by Request IP..
          return {
              "status": 403,
              "message":
              "Authentication Errors : Set Authorization Code in Header",
              "data": False
          }
      if request.httprequest.headers[
              'authorization'] != 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAvYXBpL2NsaWVudC9jYXJ0IiwiaWF0IjoxNjIyMzk2NjIxLCJleHAiOjE2MjI1Njk0MjIsIm5iZiI6MTYyMjM5NjYyMiwianRpIjoiRDJJcWxMdWp0YTBqS214UiIsInN1YiI6MywicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyIsIjAiOiJuYW1lIiwiMSI6ImVtYWlsIn0.LQzhPwfNRCiJkVNyN3qJMRNsQAKvvobSfFRPkZmL0Zw':
          return {
              "status": 403,
              "message": "Authentication Errors : not authenticate",
              "data": False
          }
      result = self._update_visit(request_body)
      return result


  def _update_visit(self, doc):
      visit = request.env['visits.visit'].sudo().browse(doc['visit_id'])
      utc_timezone = pytz.utc
      iraq_timezone = pytz.timezone('Asia/Baghdad')
      if visit:
        if doc['visit_status']=='success':
          visit.rate_visit = (100*doc['rating'])/5
          visit.state = 'done'
          if doc.get('start_date'):
            try:
              visit.start_date= (iraq_timezone.localize(datetime.strptime(doc['start_date'], '%m/%d/%Y %H:%M:%S')).astimezone(utc_timezone)).strftime('%Y-%m-%d %H:%M:%S')
            except:
              pass
          if doc.get('end_date'):
              visit.end_date= (iraq_timezone.localize(datetime.strptime(doc['end_date'], '%m/%d/%Y %H:%M:%S')).astimezone(utc_timezone)).strftime('%Y-%m-%d %H:%M:%S')
          visit.visit_status='success'
          if doc.get('note'):
             visit.visit_notes=doc['note']
        else:
          visit.state = 'done'
          if doc.get('start_date'):
            try:
              visit.start_date= (iraq_timezone.localize(datetime.strptime(doc['start_date'], '%m/%d/%Y %H:%M:%S')).astimezone(utc_timezone)).strftime('%Y-%m-%d %H:%M:%S')
            except:
              pass
          if doc.get('end_date'):
              visit.end_date= (iraq_timezone.localize(datetime.strptime(doc['end_date'], '%m/%d/%Y %H:%M:%S')).astimezone(utc_timezone)).strftime('%Y-%m-%d %H:%M:%S')
          visit.visit_status='failed'
        return {'visit': visit.id, 'status': 'done'}
      return {'visit': 0, 'status': 'failed'}

  @http.route('/api/action/create_visit',
              methods=['POST'],
              type="json",
              auth="public",
              website=True,
              csrf=False)
  def action_create_visit(self, **kw):
      request_body = request.jsonrequest
      if not request.httprequest.headers.get('authorization'):
          #  TODO Remove Static Authorization Token and add it INTO .env OR Remove Token And Check by Request IP..
          return {
              "status": 403,
              "message":
              "Authentication Errors : Set Authorization Code in Header",
              "data": False
          }
      if request.httprequest.headers[
              'authorization'] != 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAvYXBpL2NsaWVudC9jYXJ0IiwiaWF0IjoxNjIyMzk2NjIxLCJleHAiOjE2MjI1Njk0MjIsIm5iZiI6MTYyMjM5NjYyMiwianRpIjoiRDJJcWxMdWp0YTBqS214UiIsInN1YiI6MywicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyIsIjAiOiJuYW1lIiwiMSI6ImVtYWlsIn0.LQzhPwfNRCiJkVNyN3qJMRNsQAKvvobSfFRPkZmL0Zw':
          return {
              "status": 403,
              "message": "Authentication Errors : not authenticate",
              "data": False
          }
      visit_planning = request.env['visits.planning'].sudo().search([('salesperson_id', '=', request_body['user_id']),
                                                        ('start_date', '<=', datetime.now()),
                                                        ('end_date', '>=', datetime.now()),
                                                        ('state', '=', 'confirmed')],limit=1)
      if not visit_planning:
        visit_planning =request.env['visits.planning'].sudo().create({
          'salesperson_id':request_body['user_id'],
          'start_date':datetime.now(),
          'end_date':datetime.now()+relativedelta.relativedelta(months=1),
        })
        visit_planning.action_confirmed()
      visit =request.env['visits.visit'].sudo().create({
          'partner_id':request_body['partner_id'],
          'salesperson_id':request_body['user_id'],
          'visiting_date':datetime.now(),
          'visiting_day':datetime.now().strftime('%A'),
          'visit_planning_id':visit_planning.id,
        })
      visit.action_confirmed()
      visit.state='inprogress'
      visit.start_date = datetime.now()
      utc_timezone = pytz.utc
      iraq_timezone = pytz.timezone('Asia/Baghdad')
      return {
          'user_id': visit.salesperson_id.id,
          'visit_id': visit.id,
          'partner_id': visit.partner_id.id,
          'code': visit.name,
          'plannign': visit.visit_planning_id.name,
          'visiting_date':str(visit.visiting_date),
          'start_date': utc_timezone.localize(visit.start_date).astimezone(iraq_timezone).strftime('%Y-%m-%d %H:%M:%S') if visit.start_date else '',
          'state':visit.state
      }


  @http.route('/api/visits/logs', methods=['POST'], type="json", auth="public", website=True, csrf=False)
  def get_partner_visits_logs(self, **kw):
    request_body = request.jsonrequest
    if not request.httprequest.headers.get('authorization'):
      #  TODO Remove Static Authorization Token and add it INTO .env OR Remove Token And Check by Request IP..
      return {
          "status": 403,
          "message": "Authentication Errors : Set Authorization Code in Header",
          "data": False
      }
    if request.httprequest.headers[
        'authorization'] != 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAvYXBpL2NsaWVudC9jYXJ0IiwiaWF0IjoxNjIyMzk2NjIxLCJleHAiOjE2MjI1Njk0MjIsIm5iZiI6MTYyMjM5NjYyMiwianRpIjoiRDJJcWxMdWp0YTBqS214UiIsInN1YiI6MywicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyIsIjAiOiJuYW1lIiwiMSI6ImVtYWlsIn0.LQzhPwfNRCiJkVNyN3qJMRNsQAKvvobSfFRPkZmL0Zw':
      return {"status": 403, "message": "Authentication Errors : not authenticate", "data": False}
    domain = [('salesperson_id', '=', request_body['user_id']),
                                                        ('visiting_date', '<=', datetime.now()),
                                                         ('visiting_date', '>=', datetime.now()-relativedelta.relativedelta(months=1)),
                                                        ('state', 'in', ['confirmed','done','inprogress'])]
    if request_body.get('partner_id'):
      domain.append(('partner_id','=',request_body['partner_id']))
    visits = request.env['visits.visit'].sudo().search(domain,order="visiting_date desc")
    visits_lst = []
    for visit in visits:
      visits_lst.append({
          'user_id': visit.salesperson_id.id,
          'visit_id': visit.id,
          'visit': visit.name,
          'partner': {
            'id':visit.partner_id.id,
            'name':visit.partner_id.name,
            'phone': str(visit.partner_id.phone if visit.partner_id.phone else ''),
            'street': str(visit.partner_id.street if visit.partner_id.street else ''),
          },
          'code': visit.name,
          'plannign': visit.visit_planning_id.name,
          'visiting_date':str(visit.visiting_date),
          'state':visit.state,
          'visit_status':visit.visit_status if visit.visit_status else '',
      })

    return visits_lst



  @http.route('/api/visits-status', methods=['POST'], type="json", auth="public", website=True, csrf=False)
  def get_partner_visits_status(self, **kw):
    request_body = request.jsonrequest
    if not request.httprequest.headers.get('authorization'):
      #  TODO Remove Static Authorization Token and add it INTO .env OR Remove Token And Check by Request IP..
      return {
          "status": 403,
          "message": "Authentication Errors : Set Authorization Code in Header",
          "data": False
      }
    if request.httprequest.headers[
        'authorization'] != 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAvYXBpL2NsaWVudC9jYXJ0IiwiaWF0IjoxNjIyMzk2NjIxLCJleHAiOjE2MjI1Njk0MjIsIm5iZiI6MTYyMjM5NjYyMiwianRpIjoiRDJJcWxMdWp0YTBqS214UiIsInN1YiI6MywicHJ2IjoiMjNiZDVjODk0OWY2MDBhZGIzOWU3MDFjNDAwODcyZGI3YTU5NzZmNyIsIjAiOiJuYW1lIiwiMSI6ImVtYWlsIn0.LQzhPwfNRCiJkVNyN3qJMRNsQAKvvobSfFRPkZmL0Zw':
      return {"status": 403, "message": "Authentication Errors : not authenticate", "data": False}
    domain = [('salesperson_id', '=', request_body['user_id']),('state','not in',['draft','canceled']),
                                                        ('visiting_date', '=', datetime.now())]
    visits = request.env['visits.visit'].sudo().search(domain,order="visiting_date desc")
    if visits:
      return {'total':len(visits),'done':len(visits.filtered(lambda v: v.state == 'done'))}
    return {'total':0,'done':0}

