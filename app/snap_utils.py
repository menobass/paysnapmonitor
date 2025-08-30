from lighthive.client import Client

# Utility to get latest post by @peak.snaps in hive-124838

from app.logging_utils import setup_logger

logger = setup_logger("paynsnapbot")


def get_latest_peaksnaps_post(client):
    posts = client.get_discussions_by_blog("peak.snaps", limit=10)
    for post in posts:
        if post.get("author") == "peak.snaps":
            return post
    return None


def user_has_valid_snap(client, parent_author, parent_permlink, username):
    post = client.get_content(parent_author, parent_permlink)
    logger.info(
        f"user_has_valid_snap: get_content({parent_author}, {parent_permlink}) returned: {post}"
    )
    if not post:
        logger.info(
            f"user_has_valid_snap: No post found for author={parent_author}, permlink={parent_permlink}"
        )
        return False
    beneficiaries = post.get("beneficiaries", [])
    logger.info(f"user_has_valid_snap: Checking beneficiaries: {beneficiaries}")
    if not beneficiaries:
        logger.info(f"user_has_valid_snap: No beneficiaries found in post: {post}")
    found = False
    for b in beneficiaries:
        logger.info(f"user_has_valid_snap: Beneficiary entry: {b}")
        if b.get("account") == "snapnpay" and b.get("weight") == 5000:
            logger.info(
                f"user_has_valid_snap: Valid snap detected for author={parent_author} with snapnpay beneficiary."
            )
            found = True
            break
    if not found:
        logger.info(
            f"user_has_valid_snap: No valid snapnpay beneficiary found. Full post: {post}"
        )
    return found
