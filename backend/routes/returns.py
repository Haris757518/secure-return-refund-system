from flask import Blueprint, request, jsonify, session
from models.user import Return
from models.audit import log_action
from datetime import datetime
import traceback

returns_bp = Blueprint('returns', __name__)

# ================= SUBMIT RETURN =================

@returns_bp.route('/returns', methods=['POST'])
def submit_return():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json()
        if not data or 'order_id' not in data or 'reason' not in data:
            return jsonify({'error': 'order_id and reason required'}), 400

        return_request = Return(
            user_id=session['user_id'],
            order_id=data['order_id'],
            reason=data['reason'],
            status='Pending',
            refund_status='Not Initiated',
            created_at=datetime.utcnow()
        )
        return_request.save()

        log_action(
            action="RETURN_CREATED",
            actor=session['user_id'],
            details=f"Return created for order {data['order_id']}",
            return_id=str(return_request._id)
        )

        return jsonify({'message': 'Return submitted'}), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ================= USER RETURNS =================

@returns_bp.route('/returns/my', methods=['GET'])
def get_my_returns():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    returns = Return.find_by_user(session['user_id'])
    return jsonify([r.to_dict() for r in returns]), 200


# ================= ADMIN RETURNS =================

@returns_bp.route('/returns/all', methods=['GET'])
def get_all_returns():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 403

    returns = Return.find_all()
    return jsonify([r.to_dict() for r in returns]), 200


# ================= APPROVE RETURN =================

@returns_bp.route('/returns/<return_id>/approve', methods=['PUT'])
def approve_return(return_id):
    try:
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({'error': 'Admin only'}), 403

        r = Return.find_by_id(return_id)
        if not r:
            return jsonify({'error': 'Return not found'}), 404

        if r.status != "Pending":
            return jsonify({'error': 'Already processed'}), 400

        # ✅ APPROVE + AUTO REFUND INITIATE
        r.status = "Approved"
        r.refund_status = "Refund Initiated"
        r.approved_at = datetime.utcnow()
        r.save()

        log_action(
            action="RETURN_APPROVED",
            actor=session['user_id'],
            details="Return approved, refund initiated",
            return_id=return_id
        )

        return jsonify({'message': 'Approved & refund initiated'}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ================= REJECT RETURN =================

@returns_bp.route('/returns/<return_id>/reject', methods=['PUT'])
def reject_return(return_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 403

    r = Return.find_by_id(return_id)
    if not r:
        return jsonify({'error': 'Return not found'}), 404

    r.status = "Rejected"
    r.refund_status = "Rejected"
    r.save()

    log_action(
        action="RETURN_REJECTED",
        actor=session['user_id'],
        details="Return rejected",
        return_id=return_id
    )

    return jsonify({'message': 'Rejected'}), 200


# ================= COMPLETE REFUND =================

@returns_bp.route('/returns/<return_id>/refund', methods=['PUT'])
def complete_refund(return_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'error': 'Admin only'}), 403

    r = Return.find_by_id(return_id)
    if not r:
        return jsonify({'error': 'Return not found'}), 404

    r.refund_status = "Refund Successful"
    r.refunded_at = datetime.utcnow()
    r.save()

    log_action(
        action="REFUND_COMPLETED",
        actor=session['user_id'],
        details="Refund completed",
        return_id=return_id
    )

    return jsonify({'message': 'Refund completed'}), 200
